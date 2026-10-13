import time
import logging
from typing import Dict, Any, List, Optional
from config import TelemetryConfig, config as default_config
from queue_manager import QueueManager
from api_client import ApplicationApiClient
from sheets_client import GoogleSheetsBackupClient

logger = logging.getLogger("RecoveryWorker")

class RecoveryWorker:
    """
    Independent retry and historical recovery worker for Raspberry Pi 4B telemetry.
    Drains local durable SQLite outbox queues to Application API and Google Sheets.
    Supports historical backfill from Google Sheets if local database is missing.
    """
    def __init__(
        self,
        queue: QueueManager,
        api_client: ApplicationApiClient,
        sheets_client: GoogleSheetsBackupClient,
        config: Optional[TelemetryConfig] = None
    ):
        self.queue = queue
        self.api_client = api_client
        self.sheets_client = sheets_client
        self.config = config or default_config

    def process_application_queue(self, batch_size: int = 25) -> int:
        """
        Drains pending records intended for the Application API in chronological order.
        Returns the number of successfully delivered records.
        """
        pending = self.queue.get_pending_application(limit=batch_size)
        if not pending:
            return 0

        logger.info(f"Draining Application API queue: {len(pending)} pending events...")
        success_ids, failed_ids = self.api_client.send_batch(pending)

        if success_ids:
            self.queue.mark_application_synced(success_ids)
            logger.info(f"Application API delivery: {len(success_ids)} synced.")

        for f_id in failed_ids:
            self.queue.record_application_failure(f_id, "API delivery failed")

        return len(success_ids)

    def process_sheets_queue(self, batch_size: int = 15) -> int:
        """
        Drains pending records intended for Google Sheets backup in chronological order.
        Returns the number of successfully backed up records.
        """
        if not self.config.enable_google_sheets:
            return 0

        pending = self.queue.get_pending_sheets(limit=batch_size)
        if not pending:
            return 0

        logger.info(f"Draining Google Sheets queue: {len(pending)} pending events...")
        success_ids, failed_ids, err = self.sheets_client.append_telemetry_batch(pending)

        if success_ids:
            self.queue.mark_sheets_synced(success_ids)
            logger.info(f"Google Sheets backup: {len(success_ids)} synced.")

        for f_id in failed_ids:
            self.queue.record_sheets_failure(f_id, err or "Sheets append failed")

        return len(success_ids)

    def backfill_from_sheets_to_application(self, limit: int = 100) -> int:
        """
        Historical disaster recovery: Fetches records from Google Sheets and backfills
        them into the local application backend without creating duplicate entries.
        """
        logger.info(f"Initiating historical backfill from Google Sheets (limit: {limit})...")
        records = self.sheets_client.fetch_historical_records(limit=limit)
        if not records:
            logger.info("No historical records found in Google Sheets to backfill.")
            return 0

        delivered = 0
        for r in records:
            # Map Google Sheets record back to TelemetryPayload structure
            payload = {
                "timestamp": str(r.get("timestamp")),
                "source": str(r.get("source", "RASPBERRY_PI")),
                "device_id": str(r.get("device_id", self.config.device_id)),
                "voltage": float(r.get("voltage", 230.0)),
                "current": float(r.get("current", 0.0)),
                "active_power_kw": float(r.get("active_power_kw", 0.0)),
                "energy_kwh": float(r.get("energy_kwh", 0.0)),
                "frequency_hz": float(r.get("frequency_hz", 50.0)),
                "power_factor": float(r.get("power_factor", 0.95)),
                "quality": str(r.get("quality", "GOOD")),
                "machine_state": str(r.get("machine_state", "RUNNING"))
            }
            success, err = self.api_client.send_telemetry(payload)
            if success:
                delivered += 1
            else:
                logger.warning(f"Backfill record failed: {err}")

        logger.info(f"Completed historical backfill: {delivered}/{len(records)} ingested.")
        return delivered
