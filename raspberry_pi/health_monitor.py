import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from config import TelemetryConfig, config as default_config
from queue_manager import QueueManager

class HealthMonitor:
    """
    Observability and diagnostic health monitor for Raspberry Pi 4B telemetry service.
    Tracks physical meter connection, API ingestion, Google Sheets cloud sync, queue depth, and disk health.
    """
    def __init__(self, queue: QueueManager, config: Optional[TelemetryConfig] = None):
        self.queue = queue
        self.config = config or default_config

        # State tracking
        self.meter_connected: bool = False
        self.last_meter_read_time: Optional[float] = None
        self.last_meter_error: Optional[str] = None
        self.total_reads_count: int = 0

        self.app_connected: bool = False
        self.last_app_sync_time: Optional[float] = None
        self.last_app_error: Optional[str] = None
        self.total_app_delivered: int = 0

        self.sheets_connected: bool = False
        self.last_sheets_sync_time: Optional[float] = None
        self.last_sheets_error: Optional[str] = None
        self.total_sheets_delivered: int = 0

    def record_meter_read(self, success: bool, error: Optional[str] = None):
        self.total_reads_count += 1
        self.meter_connected = success
        if success:
            self.last_meter_read_time = time.time()
            self.last_meter_error = None
        else:
            self.last_meter_error = error

    def record_app_sync(self, success: bool, count: int = 1, error: Optional[str] = None):
        self.app_connected = success
        if success:
            self.last_app_sync_time = time.time()
            self.total_app_delivered += count
            self.last_app_error = None
        else:
            self.last_app_error = error

    def record_sheets_sync(self, success: bool, count: int = 1, error: Optional[str] = None):
        self.sheets_connected = success
        if success:
            self.last_sheets_sync_time = time.time()
            self.total_sheets_delivered += count
            self.last_sheets_error = None
        else:
            self.last_sheets_error = error

    def get_status_summary(self) -> Dict[str, Any]:
        app_q, sheets_q = self.queue.get_queue_depth()
        disk_info = self.queue.get_disk_health()
        now = time.time()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": self.config.device_id,
            "meter": {
                "status": "ONLINE" if self.meter_connected else "ERROR",
                "seconds_since_last_read": round(now - self.last_meter_read_time, 1) if self.last_meter_read_time else None,
                "last_error": self.last_meter_error,
                "total_samples": self.total_reads_count
            },
            "application_api": {
                "status": "ONLINE" if self.app_connected else "OFFLINE",
                "target_url": self.config.get_ingest_url(),
                "queue_depth": app_q,
                "seconds_since_last_sync": round(now - self.last_app_sync_time, 1) if self.last_app_sync_time else None,
                "last_error": self.last_app_error,
                "total_delivered": self.total_app_delivered
            },
            "google_sheets": {
                "enabled": self.config.enable_google_sheets,
                "status": "ONLINE" if self.sheets_connected else ("DISABLED" if not self.config.enable_google_sheets else "OFFLINE"),
                "spreadsheet_id": self.config.google_sheets_spreadsheet_id,
                "worksheet": self.config.sheets_worksheet_name,
                "queue_depth": sheets_q,
                "seconds_since_last_sync": round(now - self.last_sheets_sync_time, 1) if self.last_sheets_sync_time else None,
                "last_error": self.last_sheets_error,
                "total_delivered": self.total_sheets_delivered
            },
            "storage": disk_info
        }

    def print_terminal_banner(self, latest_payload: Optional[Dict[str, Any]] = None):
        """Prints a professional, human-readable terminal status dashboard."""
        status = self.get_status_summary()
        meter_s = status["meter"]
        app_s = status["application_api"]
        gs_s = status["google_sheets"]
        st = status["storage"]

        now_str = datetime.now().strftime("%H:%M:%S")
        print("\n" + "=" * 80)
        print(f"🏭 FACTORY ENERGY AUTOPILOT — RASPBERRY PI 4B TELEMETRY GATEWAY  [{now_str}]")
        print("=" * 80)
        print(f"  📟 Device: {self.config.device_id} | Port: {self.config.serial_port} (ID: {self.config.meter_id}) | Polling: {self.config.poll_interval_seconds}s")
        print(f"  ⚡ Meter Status       : {'🟢 CONNECTED' if meter_s['status'] == 'ONLINE' else '🔴 ' + (meter_s['last_error'] or 'ERROR')}")
        print(f"  📡 Application API    : {'🟢 CONNECTED' if app_s['status'] == 'ONLINE' else '🟡 QUEUED / OFFLINE'} (Queue Depth: {app_s['queue_depth']}) -> {app_s['target_url']}")
        print(f"  📊 Google Sheets Sync : {'🟢 CONNECTED' if gs_s['status'] == 'ONLINE' else '🟡 QUEUED / RETRYING'} (Queue Depth: {gs_s['queue_depth']}) -> Tab: {gs_s['worksheet']}")
        print(f"  💾 Local SQLite Queue : {st['db_size_kb']} KB | Free Disk: {st['disk_free_mb']} MB ({'HEALTHY' if st['disk_healthy'] else 'LOW DISK SPACE'})")
        
        if latest_payload and latest_payload.get("quality") != "BAD":
            kw = latest_payload.get('active_power_kw', 0.0)
            v = latest_payload.get('voltage', 0.0)
            a = latest_payload.get('current', 0.0)
            pf = latest_payload.get('power_factor', 0.0)
            kwh = latest_payload.get('energy_kwh', 0.0)
            hz = latest_payload.get('frequency_hz', 50.0)
            print("-" * 80)
            print(f"  ⚡ Real Electrical Measurements (PCC Bus):")
            print(f"     Power: {kw:.3f} kW | Voltage: {v:.1f} V | Current: {a:.2f} A | PF: {pf:.3f} | Grid: {hz:.2f} Hz | Energy: {kwh:.2f} kWh")
        print("=" * 80 + "\n")
