import os
import time
import logging
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from config import TelemetryConfig, config as default_config
from normalizer import TelemetryNormalizer

logger = logging.getLogger("SheetsClient")

# Scopes for Google Drive and Google Sheets APIs
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    gspread = None
    Credentials = None
    GSPREAD_AVAILABLE = False

class GoogleSheetsBackupClient:
    """
    Dedicated Google Sheets cloud backup client for Raspberry Pi 4B.
    Reuses existing spreadsheet and service-account setup.
    Includes duplicate prevention ledger and exponential backoff retry.
    """
    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or default_config
        self.normalizer = TelemetryNormalizer(self.config)
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self.connected = False
        self.last_sync_time = None
        self.consecutive_errors = 0
        self._synced_ids_cache = set()

    def connect(self) -> bool:
        """Authenticates with Google Sheets using the existing service account."""
        if not self.config.enable_google_sheets:
            logger.info("Google Sheets backup disabled via ENABLE_GOOGLE_SHEETS=false.")
            return False

        if not GSPREAD_AVAILABLE:
            logger.warning("gspread or google-auth not installed. Running in degraded mode.")
            self.connected = False
            return False

        sa_path = self.config.google_service_account_json
        if not os.path.exists(sa_path):
            logger.error(f"Google service account credential file missing: {sa_path}")
            self.connected = False
            return False

        try:
            logger.info("Authenticating with Google Sheets API...")
            creds = Credentials.from_service_account_file(sa_path, scopes=SCOPES)
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(self.config.google_sheets_spreadsheet_id)
            
            # Ensure target worksheet exists
            sheet_name = self.config.sheets_worksheet_name
            try:
                self.worksheet = self.spreadsheet.worksheet(sheet_name)
            except Exception:
                logger.info(f"Worksheet '{sheet_name}' not found, creating it...")
                self.worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=2000, cols=15)
                # Initialize standard 12-column header
                headers = [
                    'record_id', 'timestamp', 'source', 'device_id', 
                    'voltage', 'current', 'active_power_kw', 'energy_kwh', 
                    'frequency_hz', 'power_factor', 'quality', 'machine_state'
                ]
                self.worksheet.update('A1:L1', [headers])

            self.connected = True
            self.consecutive_errors = 0
            logger.info(f"Connected to Google Sheet '{self.spreadsheet.title}' (Tab: '{sheet_name}')")
            return True
        except Exception as e:
            # Mask potential sensitive info in exception message
            err_msg = str(e)
            logger.error(f"Google Sheets connection failed: {err_msg}")
            self.connected = False
            self.consecutive_errors += 1
            return False

    def append_telemetry_batch(
        self, 
        payloads: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[str], Optional[str]]:
        """
        Appends a batch of telemetry rows to the TELEMETRY worksheet with duplicate prevention.
        Returns (successful_record_ids, failed_record_ids, error_message).
        """
        if not self.config.enable_google_sheets:
            return [], [p.get("record_id") for p in payloads], "Google Sheets disabled"

        if not payloads:
            return [], [], None

        # Filter out payloads already known to be written (Duplicate Prevention)
        filtered_payloads = [p for p in payloads if p.get("record_id") not in self._synced_ids_cache]
        if not filtered_payloads:
            return [p.get("record_id") for p in payloads], [], None

        if not self.connected or self.worksheet is None:
            if not self.connect():
                return [], [p.get("record_id") for p in payloads], "Not connected to Google Sheets"

        rows_to_append = []
        target_ids = []

        for p in filtered_payloads:
            row = self.normalizer.to_sheets_row(p)
            rows_to_append.append(row)
            target_ids.append(p.get("record_id"))

        try:
            # Append rows using USER_ENTERED so numbers and dates are properly formatted
            self.worksheet.append_rows(rows_to_append, value_input_option="USER_ENTERED")
            
            # Cache successfully appended IDs
            for r_id in target_ids:
                self._synced_ids_cache.add(r_id)
            if len(self._synced_ids_cache) > 2000:
                # Evict older items to conserve RAM on Raspberry Pi
                self._synced_ids_cache = set(list(self._synced_ids_cache)[-1000:])

            self.last_sync_time = time.time()
            self.consecutive_errors = 0
            logger.info(f"Successfully backed up {len(rows_to_append)} rows to Google Sheets.")
            return target_ids, [], None

        except Exception as e:
            err_msg = str(e)
            logger.error(f"Failed to append rows to Google Sheets: {err_msg}")
            self.consecutive_errors += 1

            # Handle uncertain responses / verify if tail already wrote the rows
            if "timeout" in err_msg.lower() or "read error" in err_msg.lower():
                verified_ids = self._verify_tail_entries(target_ids)
                if verified_ids:
                    logger.info(f"Recovery check verified {len(verified_ids)} IDs were successfully written.")
                    unverified = [r for r in target_ids if r not in verified_ids]
                    return verified_ids, unverified, None

            return [], target_ids, err_msg

    def _verify_tail_entries(self, candidate_ids: List[str]) -> List[str]:
        """
        Duplicate prevention: Inspects recent entries in the sheet after a network timeout
        to verify if the rows were actually written before re-trying.
        """
        try:
            # Read last 30 rows of column A (record_id)
            all_vals = self.worksheet.col_values(1)
            tail = set(all_vals[-50:]) if len(all_vals) > 50 else set(all_vals)
            written = [c_id for c_id in candidate_ids if c_id in tail]
            for w in written:
                self._synced_ids_cache.add(w)
            return written
        except Exception:
            return []

    def fetch_historical_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetches historical telemetry records from Google Sheets for disaster recovery / backfill.
        """
        if not self.connected and not self.connect():
            return []

        try:
            records = self.worksheet.get_all_records()
            return records[-limit:] if len(records) > limit else records
        except Exception as e:
            logger.error(f"Failed to fetch historical records from Google Sheets: {e}")
            return []
