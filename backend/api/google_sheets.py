import os
import json
import logging
from datetime import datetime, timezone
import gspread
from google.oauth2.service_account import Credentials
import threading
import time
import pandas as pd
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

class GoogleSheetsDB:
    def __init__(self):
        self.spreadsheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID")
        self.service_account_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        self.client = None
        self.spreadsheet = None
        self.connected = False
        
        # Buffers for batch writing
        self.telemetry_buffer = []
        self.buffer_lock = threading.Lock()
        
        self.last_write_time = None
        
    def connect(self):
        if not self.spreadsheet_id:
            self.spreadsheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID")
        if not self.service_account_path:
            self.service_account_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
            
        if not self.spreadsheet_id or not self.service_account_path:
            logger.warning("Google Sheets credentials not provided. Running in degraded mode.")
            return False
            
        try:
            if not os.path.exists(self.service_account_path):
                logger.error(f"Service account file not found: {self.service_account_path}")
                return False
                
            creds = Credentials.from_service_account_file(self.service_account_path, scopes=SCOPES)
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            self.connected = True
            logger.info("Successfully connected to Google Sheets.")
            
            # Ensure tabs exist
            self._ensure_tabs()
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {repr(e)}")
            self.connected = False
            return False
            
    def _ensure_tabs(self):
        required_tabs = [
            'TELEMETRY', 'ASSETS', 'FORECASTS', 'ANOMALIES', 
            'OPTIMIZATION_RUNS', 'RECOMMENDATIONS', 'EVENTS', 
            'BUSINESS_IMPACT', 'HISTORICAL_DATASET', 'APP_CONFIG'
        ]
        
        existing_tabs = [worksheet.title for worksheet in self.spreadsheet.worksheets()]
        
        for tab in required_tabs:
            if tab not in existing_tabs:
                logger.info(f"Creating missing tab: {tab}")
                worksheet = self.spreadsheet.add_worksheet(title=tab, rows=1000, cols=20)
                # Add headers based on tab type
                self._initialize_headers(worksheet, tab)
                
    def _initialize_headers(self, worksheet, tab_name: str):
        headers = {
            'TELEMETRY': ['record_id', 'timestamp', 'source', 'device_id', 'voltage', 'current', 'active_power_kw', 'energy_kwh', 'frequency_hz', 'power_factor', 'quality', 'machine_state'],
            'ASSETS': ['asset_id', 'name', 'category', 'operating_power_kw', 'idle_power_kw', 'production_dependency', 'last_updated'],
            'FORECASTS': ['record_id', 'timestamp', 'model_version', 'current_demand_kw', 'predicted_peak_kw', 'horizon_min'],
            'ANOMALIES': ['record_id', 'timestamp', 'asset_id', 'anomaly_score', 'description', 'status'],
            'OPTIMIZATION_RUNS': ['record_id', 'timestamp', 'predicted_peak_kw', 'safe_target_kw', 'optimized_peak_kw', 'status'],
            'RECOMMENDATIONS': ['record_id', 'run_id', 'asset_id', 'action', 'predicted_impact_kw', 'status'],
            'EVENTS': ['record_id', 'timestamp', 'event_type', 'source', 'description'],
            'BUSINESS_IMPACT': ['record_id', 'timestamp', 'run_id', 'peak_avoided_kw', 'cost_avoided', 'production_impact_percent', 'status'],
            'HISTORICAL_DATASET': ['date', 'Usage_kWh', 'Lagging_Current_Reactive.Power_kVarh', 'Leading_Current_Reactive_Power_kVarh', 'CO2_tCO2', 'Lagging_Current_Power_Factor', 'Leading_Current_Power_Factor', 'NSM', 'WeekStatus', 'Day_of_week', 'Load_Type'], # simplified
            'APP_CONFIG': ['config_key', 'config_value', 'updated_at']
        }
        if tab_name in headers:
            worksheet.update('A1', [headers[tab_name]])
            
    def append_telemetry(self, records: List[Dict[str, Any]]):
        with self.buffer_lock:
            self.telemetry_buffer.extend(records)
            
    def flush_telemetry(self):
        with self.buffer_lock:
            if not self.telemetry_buffer:
                return
            records_to_write = self.telemetry_buffer[:]
            self.telemetry_buffer = []
            
        if not self.connected:
            # Re-queue if not connected, but bound the size
            with self.buffer_lock:
                self.telemetry_buffer = records_to_write + self.telemetry_buffer
                if len(self.telemetry_buffer) > 10000:
                    self.telemetry_buffer = self.telemetry_buffer[-10000:]
            return
            
        try:
            worksheet = self.spreadsheet.worksheet('TELEMETRY')
            rows = []
            for r in records_to_write:
                rows.append([
                    r.get('record_id', ''),
                    r.get('timestamp', ''),
                    r.get('source', ''),
                    r.get('device_id', ''),
                    r.get('voltage', 0),
                    r.get('current', 0),
                    r.get('active_power_kw', 0),
                    r.get('energy_kwh', 0),
                    r.get('frequency_hz', 0),
                    r.get('power_factor', 0),
                    r.get('quality', ''),
                    r.get('machine_state', '')
                ])
            worksheet.append_rows(rows, value_input_option='USER_ENTERED')
            self.last_write_time = datetime.now(timezone.utc)
            logger.info(f"Flushed {len(rows)} telemetry records to Google Sheets")
        except Exception as e:
            logger.error(f"Failed to flush telemetry: {repr(e)}")
            # Re-queue on failure
            with self.buffer_lock:
                self.telemetry_buffer = records_to_write + self.telemetry_buffer
                

    def get_latest_telemetry_fallback(self) -> Optional[Dict]:
        if not self.connected:
            return None
            
        now = time.time()
        # Cache for 30 seconds
        if hasattr(self, '_latest_fallback_cache') and hasattr(self, '_latest_fallback_time'):
            if now - self._latest_fallback_time < 30:
                return self._latest_fallback_cache
                
        try:
            worksheet = self.spreadsheet.worksheet('TELEMETRY')
            # Fetch last few rows to find the most recent valid one
            all_vals = worksheet.get_all_values()
            if len(all_vals) <= 1:
                return None
                
            headers = all_vals[0]
            # Get the last row
            last_row = all_vals[-1]
            record = dict(zip(headers, last_row))
            
            self._latest_fallback_cache = record
            self._latest_fallback_time = now
            return record
        except Exception as e:
            logger.error(f"Failed to fetch fallback telemetry: {repr(e)}")
            return None

    def get_telemetry_history(self, limit=100) -> List[Dict]:
        if not self.connected:
            return []
        try:
            worksheet = self.spreadsheet.worksheet('TELEMETRY')
            # Get all records, which is slow for large sheets, so we should fetch the last N rows
            # But gspread doesn't have an easy "tail" without knowing row count
            # A simple approach for this prototype:
            all_records = worksheet.get_all_records()
            return all_records[-limit:]
        except Exception as e:
            logger.error(f"Failed to fetch telemetry history: {repr(e)}")
            return []

    def get_historical_dataset(self) -> pd.DataFrame:
        if not self.connected:
            # Fallback to empty DF if offline to not crash the ML
            return pd.DataFrame(columns=['timestamp', 'total_demand_kw'])
        try:
            worksheet = self.spreadsheet.worksheet('HISTORICAL_DATASET')
            records = worksheet.get_all_records()
            return pd.DataFrame(records)
        except Exception as e:
            logger.error(f"Failed to fetch historical dataset: {repr(e)}")
            return pd.DataFrame(columns=['timestamp', 'total_demand_kw'])

# Global instance
    def log_optimization_run(self, opt_data: dict, recommendations: List[dict]):
        if not self.connected:
            return
        try:
            worksheet_opt = self.spreadsheet.worksheet('OPTIMIZATION_RUNS')
            worksheet_rec = self.spreadsheet.worksheet('RECOMMENDATIONS')
            
            run_id = opt_data.get('record_id')
            worksheet_opt.append_row([
                run_id,
                opt_data.get('timestamp'),
                opt_data.get('predicted_peak_kw', 0),
                opt_data.get('safe_target_kw', 0),
                opt_data.get('optimized_peak_kw', 0),
                opt_data.get('status', '')
            ], value_input_option='USER_ENTERED')
            
            rec_rows = []
            for r in recommendations:
                rec_rows.append([
                    r.get('record_id', ''),
                    run_id,
                    r.get('asset_id', ''),
                    r.get('action', ''),
                    r.get('predicted_impact_kw', 0),
                    r.get('status', '')
                ])
                
            if rec_rows:
                worksheet_rec.append_rows(rec_rows, value_input_option='USER_ENTERED')
            
            logger.info(f"Logged optimization run {run_id}")
        except Exception as e:
            logger.error(f"Failed to log optimization run: {repr(e)}")


gsheets_db = GoogleSheetsDB()

def background_flush_task():
    while True:
        time.sleep(10)
        gsheets_db.flush_telemetry()
        
# Start background thread
flush_thread = threading.Thread(target=background_flush_task, daemon=True)
flush_thread.start()


