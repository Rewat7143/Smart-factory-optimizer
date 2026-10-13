#!/usr/bin/env python3
"""
Factory Energy Autopilot — Edge Telemetry & Relay Control Service.

Main runtime entrypoint:
  1. Reads real-time measurements from L&T WL 4400 Multi-Function Meter via hardware adapter.
  2. Evaluates 3-relay peak-demand state machine (strictly MONITOR_ONLY by default).
  3. Sends canonical telemetry to existing FastAPI backend (POST /api/telemetry/ingest).
  4. Backs up readings to existing Google Sheet (tab: TELEMETRY).
  5. Queues readings in local SQLite outbox during outages and drains backlog chronologically.

Single command to run on Raspberry Pi:
  python3 main.py
"""

import os
import sys
import time
import signal
import argparse
import logging
from typing import Optional

from config import TelemetryConfig, config as default_config
from hardware_adapters import (
    BaseMeterAdapter,
    BaseRelayAdapter,
    create_meter_adapter,
    create_relay_adapter
)
from relay_control import RelayController, RelayState
from normalizer import TelemetryNormalizer
from queue_manager import QueueManager
from api_client import ApplicationApiClient
from sheets_client import GoogleSheetsBackupClient
from recovery_worker import RecoveryWorker
from health_monitor import HealthMonitor

# Configure industrial log format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-15s | %(levelname)-7s | %(message)s"
)
logger = logging.getLogger("TelemetryMain")


class TelemetryService:
    """
    Unified runtime daemon for Factory Energy Autopilot edge node.
    Combines meter data acquisition, peak-demand relay state machine,
    FastAPI ingestion, Google Sheets cloud backup, and offline SQLite buffering.
    """

    def __init__(self, config: Optional[TelemetryConfig] = None, monitor_only: Optional[bool] = None):
        self.config = config or default_config
        self.running = False

        # 1. Hardware Adapters
        self.meter_adapter: BaseMeterAdapter = create_meter_adapter(self.config)
        self.relay_adapter: BaseRelayAdapter = create_relay_adapter(self.config)

        # 2. Relay Controller (strict MONITOR_ONLY safety default)
        is_monitor = monitor_only if monitor_only is not None else self.config.relay_monitor_only
        self.relay_controller = RelayController(
            adapter=self.relay_adapter,
            config=self.config,
            monitor_only=is_monitor
        )

        # 3. Telemetry Pipeline & Local Outbox
        self.queue = QueueManager(self.config)
        self.normalizer = TelemetryNormalizer(self.config)
        self.api_client = ApplicationApiClient(self.config)
        self.sheets_client = GoogleSheetsBackupClient(self.config)
        self.recovery_worker = RecoveryWorker(
            self.queue, self.api_client, self.sheets_client, self.config
        )
        self.health_monitor = HealthMonitor(self.queue, self.config)

        # 4. Buffering and Timers
        self.last_sheets_flush = time.time()
        self.last_purge_time = time.time()
        self.sheets_buffer = []

    def start(self):
        """Runs the complete edge acquisition, relay evaluation, and streaming loop."""
        self.running = True
        self._register_signals()

        logger.info("=" * 75)
        logger.info("  FACTORY ENERGY AUTOPILOT — EDGE TELEMETRY & RELAY DAEMON")
        logger.info("=" * 75)
        logger.info(f" Platform       : {self.config.hardware_platform}")
        logger.info(f" Meter Interface: {self.config.serial_port} (ID: {self.config.meter_id}, {self.config.baudrate} baud)")
        logger.info(f" Target API     : {self.config.get_ingest_url()}")
        logger.info(f" Google Sheets  : {'ENABLED' if self.config.enable_google_sheets else 'DISABLED'}")
        logger.info(f" Relay Mode     : {'MONITOR_ONLY (Safe)' if self.relay_controller.monitor_only else 'ACTIVE (Hardware Powered)'}")
        logger.info(f" Peak Threshold : {self.config.peak_demand_threshold_kw} kW")
        logger.info(f" SQLite Queue   : {self.config.sqlite_db_path}")
        logger.info("=" * 75)

        # Validate configuration
        warnings = self.config.validate()
        for w in warnings:
            logger.warning(f"Config notice: {w}")

        # Connect hardware & cloud services
        meter_connected = self.meter_adapter.connect()
        if not meter_connected and not self.config.mock_hardware:
            logger.warning("[Main] Meter connection deferred; daemon will retry during loop iterations.")

        if self.config.enable_google_sheets:
            self.sheets_client.connect()

        # Startup recovery: drain pending items from previous offline sessions
        logger.info("Performing startup recovery check on SQLite queue...")
        drained_app = self.recovery_worker.process_application_queue(batch_size=50)
        drained_sheets = self.recovery_worker.process_sheets_queue(batch_size=50)
        if drained_app > 0 or drained_sheets > 0:
            logger.info(f"Startup recovery: Drained {drained_app} app events, {drained_sheets} sheets events.")

        logger.info(f"Entering continuous telemetry loop (Sampling Interval: {self.config.poll_interval_seconds}s)...")
        while self.running:
            loop_start = time.time()
            try:
                self._iteration()
            except Exception as e:
                logger.error(f"Iteration error: {e}", exc_info=True)

            elapsed = time.time() - loop_start
            sleep_time = max(0.1, self.config.poll_interval_seconds - elapsed)
            time.sleep(sleep_time)

        self._shutdown()

    def _iteration(self):
        # 1. Acquire real meter measurements from hardware adapter
        read_result = self.meter_adapter.read_all_parameters()
        self.health_monitor.record_meter_read(read_result.success, read_result.error)

        # 2. Normalize to canonical JSON schema
        payload = self.normalizer.normalize(read_result)

        # 3. Evaluate 3-relay peak-demand state machine
        active_kw = payload.get("active_power_kw", 0.0)
        relay_decision = self.relay_controller.evaluate_demand(active_kw)

        # Attach relay state to telemetry metadata
        payload["machine_state"] = "RUNNING" if active_kw > 0.1 else "IDLE"
        payload["relay_decision"] = relay_decision

        # 4. Enqueue to durable local SQLite queue (WAL mode) BEFORE attempting network
        self.queue.enqueue(payload)

        # 5. Forward to FastAPI backend
        api_success, api_err = self.api_client.send_telemetry(payload)
        if api_success:
            self.queue.mark_application_synced([payload["record_id"]])
            self.health_monitor.record_app_sync(True, count=1)
        else:
            self.queue.record_application_failure(payload["record_id"], api_err or "API Error")
            self.health_monitor.record_app_sync(False, error=api_err)

        # 6. Buffer and batch write to Google Sheets backup
        if self.config.enable_google_sheets:
            self.sheets_buffer.append(payload)
            now = time.time()
            if (len(self.sheets_buffer) >= self.config.sheets_batch_size or 
                (now - self.last_sheets_flush) >= self.config.sheets_flush_interval_seconds):
                self._flush_sheets()

        # 7. Drain historical offline queue if network link has recovered
        app_depth, sheets_depth = self.queue.get_queue_depth()
        if app_depth > 0:
            self.recovery_worker.process_application_queue(batch_size=25)
        if sheets_depth > 0 and self.config.enable_google_sheets:
            self.recovery_worker.process_sheets_queue(batch_size=15)

        # 8. Industrial terminal banner output every 10 samples
        if self.health_monitor.total_reads_count % 10 == 0:
            self.health_monitor.print_terminal_banner(payload)

        # 9. Daily purge of fully synchronized queue entries
        if time.time() - self.last_purge_time > 86400:
            purged = self.queue.purge_synced_records()
            if purged > 0:
                logger.info(f"Purged {purged} synced records from SQLite ledger.")
            self.last_purge_time = time.time()

    def _flush_sheets(self):
        if not self.sheets_buffer:
            return
        batch = self.sheets_buffer[:]
        self.sheets_buffer = []
        self.last_sheets_flush = time.time()

        success_ids, failed_ids, err = self.sheets_client.append_telemetry_batch(batch)
        if success_ids:
            self.queue.mark_sheets_synced(success_ids)
            self.health_monitor.record_sheets_sync(True, count=len(success_ids))
        if failed_ids:
            for fid in failed_ids:
                self.queue.record_sheets_failure(fid, err or "Sheets append failed")
            self.health_monitor.record_sheets_sync(False, error=err)

    def _register_signals(self):
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

    def _handle_exit(self, signum, frame):
        logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.running = False

    def _shutdown(self):
        logger.info("Cleaning up subsystems...")
        self._flush_sheets()
        self.relay_controller.emergency_restore_all()
        self.relay_controller.cleanup()
        self.meter_adapter.disconnect()
        logger.info("Daemon stopped safely. SQLite queue persisted on disk.")


def parse_args():
    parser = argparse.ArgumentParser(description="Factory Energy Autopilot Edge Telemetry Daemon")
    parser.add_argument("--mock", action="store_true", help="Run with mock hardware for dry-run testing")
    parser.add_argument("--monitor-only", action="store_true", help="Force relay controller into safe MONITOR_ONLY mode")
    parser.add_argument("--active-relays", action="store_true", help="Enable physical relay pin actuation (Safety override)")
    parser.add_argument("--platform", choices=["RPI4B", "UNO_Q", "VIRTUAL"], help="Override hardware platform adapter")
    parser.add_argument("--drain-queue", action="store_true", help="Process pending SQLite backlog and exit")
    parser.add_argument("--backfill-from-sheets", action="store_true", help="Recover history from Google Sheets and exit")
    parser.add_argument("--limit", type=int, default=100, help="Max records for backfill/drain")
    return parser.parse_args()


def main():
    args = parse_args()
    cfg = TelemetryConfig()

    if args.mock:
        cfg.mock_hardware = True
    if args.platform:
        cfg.hardware_platform = args.platform

    monitor_only = True
    if args.active_relays:
        monitor_only = False
    elif args.monitor_only:
        monitor_only = True

    if args.drain_queue:
        logger.info("Running manual offline queue drain...")
        queue = QueueManager(cfg)
        api = ApplicationApiClient(cfg)
        sheets = GoogleSheetsBackupClient(cfg)
        recovery = RecoveryWorker(queue, api, sheets, cfg)
        app_drained = recovery.process_application_queue(batch_size=args.limit)
        sheets_drained = recovery.process_sheets_queue(batch_size=args.limit)
        logger.info(f"Drained {app_drained} application records, {sheets_drained} sheets records.")
        sys.exit(0)

    if args.backfill_from_sheets:
        logger.info("Running historical backfill from Google Sheets...")
        queue = QueueManager(cfg)
        api = ApplicationApiClient(cfg)
        sheets = GoogleSheetsBackupClient(cfg)
        recovery = RecoveryWorker(queue, api, sheets, cfg)
        backfilled = recovery.backfill_application_from_sheets(limit=args.limit)
        logger.info(f"Backfilled {backfilled} historical records from Google Sheets into application.")
        sys.exit(0)

    service = TelemetryService(config=cfg, monitor_only=monitor_only)
    service.start()


if __name__ == "__main__":
    main()
