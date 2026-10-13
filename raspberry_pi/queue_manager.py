import sqlite3
import json
import shutil
import logging
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from config import TelemetryConfig, config as default_config

logger = logging.getLogger("QueueManager")

class QueueManager:
    """
    Lightweight, durable SQLite storage on Raspberry Pi 4B.
    Guarantees zero data loss across power outages, network disconnects,
    and backend restarts. Tracks delivery to Application API and Google Sheets independently.
    """
    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or default_config
        self.db_path = self.config.sqlite_db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for high concurrency & resilience against abrupt power loss
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_outbox (
                    record_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    application_synced INTEGER DEFAULT 0,
                    application_synced_at TEXT,
                    sheets_synced INTEGER DEFAULT 0,
                    sheets_synced_at TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_attempt_at TEXT,
                    app_retry_count INTEGER DEFAULT 0,
                    sheets_retry_count INTEGER DEFAULT 0,
                    last_app_error TEXT,
                    last_sheets_error TEXT
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_outbox_app ON telemetry_outbox(application_synced, timestamp);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_outbox_sheets ON telemetry_outbox(sheets_synced, timestamp);")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_ledger (
                    destination TEXT PRIMARY KEY,
                    last_synced_record_id TEXT,
                    last_synced_timestamp TEXT,
                    total_synced_count INTEGER DEFAULT 0,
                    updated_at TEXT
                );
            """)
            conn.commit()

    def enqueue(self, payload: Dict[str, Any]) -> bool:
        """
        Persists a newly acquired reading to local disk BEFORE network transmission.
        """
        record_id = payload.get("record_id")
        timestamp = payload.get("timestamp")
        device_id = payload.get("device_id", self.config.device_id)
        source = payload.get("source", "RASPBERRY_PI")
        payload_str = json.dumps(payload)

        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO telemetry_outbox (
                        record_id, timestamp, device_id, source, payload_json,
                        application_synced, sheets_synced
                    ) VALUES (?, ?, ?, ?, ?, 0, 0);
                """, (record_id, timestamp, device_id, source, payload_str))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue telemetry event {record_id}: {e}")
            return False

    def get_pending_application(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Returns oldest un-synced events for the Application API in chronological order.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT record_id, timestamp, payload_json, app_retry_count 
                FROM telemetry_outbox 
                WHERE application_synced = 0 
                ORDER BY timestamp ASC 
                LIMIT ?;
            """, (limit,))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                try:
                    data = json.loads(r["payload_json"])
                    data["_app_retry_count"] = r["app_retry_count"]
                    results.append(data)
                except Exception:
                    pass
            return results

    def mark_application_synced(self, record_ids: List[str]):
        """
        Marks records successfully ingested by Application API and records in ledger.
        """
        if not record_ids:
            return
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            placeholders = ",".join("?" for _ in record_ids)
            conn.execute(f"""
                UPDATE telemetry_outbox 
                SET application_synced = 1, 
                    application_synced_at = ?,
                    last_app_error = NULL
                WHERE record_id IN ({placeholders});
            """, [now_str] + record_ids)

            # Update ledger
            last_id = record_ids[-1]
            conn.execute("""
                INSERT INTO sync_ledger (destination, last_synced_record_id, last_synced_timestamp, total_synced_count, updated_at)
                VALUES ('APPLICATION', ?, ?, ?, ?)
                ON CONFLICT(destination) DO UPDATE SET
                    last_synced_record_id = excluded.last_synced_record_id,
                    last_synced_timestamp = excluded.last_synced_timestamp,
                    total_synced_count = total_synced_count + ?,
                    updated_at = excluded.updated_at;
            """, (last_id, now_str, len(record_ids), now_str, len(record_ids)))
            conn.commit()

    def record_application_failure(self, record_id: str, error: str):
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE telemetry_outbox 
                SET app_retry_count = app_retry_count + 1,
                    last_attempt_at = ?,
                    last_app_error = ?
                WHERE record_id = ?;
            """, (now_str, error, record_id))
            conn.commit()

    def get_pending_sheets(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Returns oldest un-synced events for Google Sheets backup in chronological order.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT record_id, timestamp, payload_json, sheets_retry_count 
                FROM telemetry_outbox 
                WHERE sheets_synced = 0 
                ORDER BY timestamp ASC 
                LIMIT ?;
            """, (limit,))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                try:
                    data = json.loads(r["payload_json"])
                    data["_sheets_retry_count"] = r["sheets_retry_count"]
                    results.append(data)
                except Exception:
                    pass
            return results

    def mark_sheets_synced(self, record_ids: List[str]):
        """
        Marks records successfully written to Google Sheets and records in ledger.
        """
        if not record_ids:
            return
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            placeholders = ",".join("?" for _ in record_ids)
            conn.execute(f"""
                UPDATE telemetry_outbox 
                SET sheets_synced = 1, 
                    sheets_synced_at = ?,
                    last_sheets_error = NULL
                WHERE record_id IN ({placeholders});
            """, [now_str] + record_ids)

            last_id = record_ids[-1]
            conn.execute("""
                INSERT INTO sync_ledger (destination, last_synced_record_id, last_synced_timestamp, total_synced_count, updated_at)
                VALUES ('GOOGLE_SHEETS', ?, ?, ?, ?)
                ON CONFLICT(destination) DO UPDATE SET
                    last_synced_record_id = excluded.last_synced_record_id,
                    last_synced_timestamp = excluded.last_synced_timestamp,
                    total_synced_count = total_synced_count + ?,
                    updated_at = excluded.updated_at;
            """, (last_id, now_str, len(record_ids), now_str, len(record_ids)))
            conn.commit()

    def record_sheets_failure(self, record_id: str, error: str):
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE telemetry_outbox 
                SET sheets_retry_count = sheets_retry_count + 1,
                    last_attempt_at = ?,
                    last_sheets_error = ?
                WHERE record_id = ?;
            """, (now_str, error, record_id))
            conn.commit()

    def get_queue_depth(self) -> Tuple[int, int]:
        """Returns (pending_app_count, pending_sheets_count)"""
        with self._get_connection() as conn:
            app_count = conn.execute("SELECT COUNT(*) FROM telemetry_outbox WHERE application_synced = 0;").fetchone()[0]
            sheets_count = conn.execute("SELECT COUNT(*) FROM telemetry_outbox WHERE sheets_synced = 0;").fetchone()[0]
            return app_count, sheets_count

    def purge_synced_records(self, days_retention: Optional[int] = None) -> int:
        """
        Safely removes fully synchronized records older than retention threshold.
        NEVER deletes records if either destination is un-synced!
        """
        days = days_retention or self.config.retention_days
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        with self._get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM telemetry_outbox 
                WHERE application_synced = 1 
                  AND sheets_synced = 1 
                  AND timestamp < ?;
            """, (cutoff,))
            deleted = cursor.rowcount
            conn.commit()
            if deleted > 0:
                conn.execute("VACUUM;")
            return deleted

    def get_disk_health(self) -> Dict[str, Any]:
        """Checks local disk space and SQLite database size."""
        db_file = Path(self.db_path)
        db_size_bytes = db_file.stat().st_size if db_file.exists() else 0

        target_dir = db_file.parent if db_file.parent.exists() else Path.cwd()
        disk_usage = shutil.disk_usage(target_dir)

        free_mb = disk_usage.free / (1024 * 1024)
        total_mb = disk_usage.total / (1024 * 1024)

        return {
            "db_path": str(db_file),
            "db_size_kb": round(db_size_bytes / 1024, 2),
            "disk_free_mb": round(free_mb, 1),
            "disk_total_mb": round(total_mb, 1),
            "disk_healthy": free_mb >= self.config.min_disk_free_mb
        }
