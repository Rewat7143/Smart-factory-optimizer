import os
from pathlib import Path
from typing import Optional

# Try loading .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    # Look for .env in current directory, parent directory, and backend
    env_paths = [
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent / ".env",
        Path(__file__).parent.parent / "backend" / ".env"
    ]
    for p in env_paths:
        if p.exists():
            load_dotenv(p)
            break
except ImportError:
    pass

class TelemetryConfig:
    """
    Centralized configuration for Raspberry Pi 4B telemetry service.
    All properties are configurable via environment variables without editing source code.
    """
    def __init__(self):
        # 1. Physical L&T Energy Meter (RS-485 / Modbus RTU)
        self.serial_port: str = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
        self.meter_id: int = int(os.getenv("METER_ID", "34"))
        self.baudrate: int = int(os.getenv("BAUDRATE", "9600"))
        self.bytesize: int = int(os.getenv("BYTESIZE", "8"))
        self.parity: str = os.getenv("PARITY", "EVEN").upper()  # 'EVEN', 'NONE', 'ODD'
        self.stopbits: int = int(os.getenv("STOPBITS", "1"))
        self.timeout_seconds: float = float(os.getenv("METER_TIMEOUT_SECONDS", "2.0"))
        self.poll_interval_seconds: float = float(os.getenv("POLL_INTERVAL_SECONDS", "2.0"))
        
        # Test mode flag: if True, provides realistic mock readings when RS-485 hardware is not attached
        # In production on the Raspberry Pi, this MUST be False.
        self.mock_hardware: bool = os.getenv("MOCK_HARDWARE", "false").lower() in ("true", "1", "yes")

        # 2. Existing Smart Factory Energy Autopilot Backend API
        self.api_base_url: str = os.getenv(
            "ENERGY_API_BASE_URL", 
            os.getenv("API_BASE_URL", "http://localhost:8000")
        ).rstrip("/")
        self.telemetry_endpoint: str = os.getenv("TELEMETRY_ENDPOINT", "/api/telemetry/ingest")
        self.health_endpoint: str = os.getenv("HEALTH_ENDPOINT", "/api/system/status")
        self.device_id: str = os.getenv("DEVICE_ID", "RPi-METER-01")
        self.api_timeout_seconds: float = float(os.getenv("API_TIMEOUT_SECONDS", "5.0"))

        # 3. Existing Google Sheets Cloud Backup
        self.enable_google_sheets: bool = os.getenv("ENABLE_GOOGLE_SHEETS", "true").lower() in ("true", "1", "yes")
        self.google_sheets_spreadsheet_id: str = os.getenv(
            "GOOGLE_SHEETS_SPREADSHEET_ID", 
            "1_ncPDlztJQT71G8hxazyF-EYrEvzwi8h_2BRPLXP5nQ"
        )
        self.google_service_account_json: str = self._resolve_service_account_path()
        self.sheets_worksheet_name: str = os.getenv("SHEETS_WORKSHEET_NAME", "TELEMETRY")
        self.sheets_batch_size: int = int(os.getenv("SHEETS_BATCH_SIZE", "10"))
        self.sheets_flush_interval_seconds: float = float(os.getenv("SHEETS_FLUSH_INTERVAL_SECONDS", "10.0"))

        # 4. Local Durable Queue (SQLite on Raspberry Pi)
        default_db = str(Path(__file__).parent / "telemetry_queue.db")
        self.sqlite_db_path: str = os.getenv("SQLITE_DB_PATH", default_db)
        self.retention_days: int = int(os.getenv("MAX_QUEUE_RETENTION_DAYS", "7"))
        self.max_batch_size: int = int(os.getenv("MAX_BATCH_SIZE", "50"))
        self.min_disk_free_mb: int = int(os.getenv("MIN_DISK_FREE_MB", "100"))

        # 5. Hardware Platform & Adapters (RPI4B today, UNO_Q tomorrow)
        self.hardware_platform: str = os.getenv("HARDWARE_PLATFORM", "RPI4B").upper()  # 'RPI4B', 'UNO_Q', 'VIRTUAL'

        # 6. Relay Control & Peak-Demand State Machine (Strictly MONITOR_ONLY by default)
        # Never invent GPIO pins, relay polarity, or peak-demand thresholds
        self.relay_mode: str = os.getenv("RELAY_MODE", "MONITOR_ONLY").upper()  # 'MONITOR_ONLY' or 'ACTIVE'
        self.relay_monitor_only: bool = (self.relay_mode != "ACTIVE")

        # Relay GPIO Pin Mapping (None if unconfigured)
        self.relay_1_pin: Optional[int] = self._parse_optional_int(os.getenv("RELAY_1_PIN"))
        self.relay_2_pin: Optional[int] = self._parse_optional_int(os.getenv("RELAY_2_PIN"))
        self.relay_3_pin: Optional[int] = self._parse_optional_int(os.getenv("RELAY_3_PIN"))
        self.relay_active_low: bool = os.getenv("RELAY_ACTIVE_LOW", "true").lower() in ("true", "1", "yes")

        # Peak-Demand State Machine Thresholds (None if unconfigured)
        self.peak_demand_threshold_kw: Optional[float] = self._parse_optional_float(os.getenv("PEAK_DEMAND_THRESHOLD_KW"))
        self.warning_threshold_ratio: float = float(os.getenv("WARNING_THRESHOLD_RATIO", "0.90"))
        self.restore_hysteresis_kw: float = float(os.getenv("RESTORE_HYSTERESIS_KW", "5.0"))
        self.min_trip_time_seconds: float = float(os.getenv("MIN_TRIP_TIME_SECONDS", "30.0"))
        self.min_restart_delay_seconds: float = float(os.getenv("MIN_RESTART_DELAY_SECONDS", "10.0"))

        # 7. Logging
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_file: Optional[str] = os.getenv("LOG_FILE", str(Path(__file__).parent / "telemetry_service.log"))

    @staticmethod
    def _parse_optional_int(val: Optional[str]) -> Optional[int]:
        if val is None or val.strip() == "":
            return None
        try:
            return int(val.strip())
        except ValueError:
            return None

    @staticmethod
    def _parse_optional_float(val: Optional[str]) -> Optional[float]:
        if val is None or val.strip() == "":
            return None
        try:
            return float(val.strip())
        except ValueError:
            return None

    def _resolve_service_account_path(self) -> str:
        explicit = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if explicit and os.path.exists(explicit):
            return explicit
            
        candidates = [
            Path(__file__).parent / "service-account.json",
            Path(__file__).parent.parent / "backend" / "service-account.json",
            Path(__file__).parent.parent / "smart-factory-optimization-66edb227cd0b.json",
            Path(__file__).parent.parent.parent / "smart-factory-optimization-66edb227cd0b.json",
            Path.cwd() / "service-account.json",
        ]
        for c in candidates:
            if c.exists():
                return str(c.resolve())
        return explicit or "service-account.json"

    def get_ingest_url(self) -> str:
        return f"{self.api_base_url}{self.telemetry_endpoint}"

    def get_health_url(self) -> str:
        return f"{self.api_base_url}{self.health_endpoint}"

    def validate(self) -> list:
        """Returns a list of configuration warnings or errors."""
        issues = []
        if not self.api_base_url:
            issues.append("API_BASE_URL is empty")
        if self.enable_google_sheets:
            if not self.google_sheets_spreadsheet_id:
                issues.append("GOOGLE_SHEETS_SPREADSHEET_ID is missing")
            if not os.path.exists(self.google_service_account_json):
                issues.append(f"Google service account file not found at: {self.google_service_account_json}")
        return issues

config = TelemetryConfig()
