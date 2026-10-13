import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from api.google_sheets import gsheets_db
import logging

logger = logging.getLogger(__name__)

class HistoryGenerator:
    """Provides historical data for the factory, backed by Google Sheets."""
    def __init__(self, factory_model, days: int = 30, interval_min: int = 15):
        self.factory = factory_model
        self.days = days
        self.interval_min = interval_min
        self.history_df = None
        
    def generate(self) -> pd.DataFrame:
        logger.info("Fetching historical data from Google Sheets...")
        
        # In a real environment we would load purely from Google Sheets.
        # But if the sheet is empty or offline, we must provide a fallback dataframe structure 
        # so the app doesn't crash, but per user instructions we shouldn't "invent" data.
        # Let's try to fetch from GSheets.
        df = gsheets_db.get_historical_dataset()
        
        if df.empty:
            logger.warning("Google Sheets returned empty historical dataset. Providing zeroed fallback to prevent crash.")
            end_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            start_time = end_time - timedelta(days=self.days)
            timestamps = pd.date_range(start=start_time, end=end_time, freq=f'{self.interval_min}min')
            n_samples = len(timestamps)
            
            data = {
                'timestamp': timestamps,
                'temperature_c': np.zeros(n_samples),
                'production_target_percent': np.zeros(n_samples),
                'total_demand_kw': np.zeros(n_samples),
                'production_rate': np.zeros(n_samples)
            }
            
            for asset_id in self.factory.assets:
                data[f'{asset_id}_power'] = np.zeros(n_samples)
                
            self.history_df = pd.DataFrame(data)
        else:
            # Parse timestamps
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            self.history_df = df
            
        
        return self.history_df

    def get_history(self) -> pd.DataFrame:

        if self.history_df is None:
            self.generate()
        return self.history_df
    def append_reading(self, timestamp, power_kw, production_percent):
        if self.history_df is not None:
            new_data = {
                'timestamp': [pd.to_datetime(timestamp)],
                'total_demand_kw': [power_kw],
                'production_percent': [production_percent],
                'temperature_c': [self.factory.temperature_c]
            }
            # Append individual asset powers
            for asset_id, asset in self.factory.assets.items():
                new_data[f'{asset_id}_power'] = [asset.get_current_power()]
                
            new_row = pd.DataFrame(new_data)
            self.history_df = pd.concat([self.history_df, new_row], ignore_index=True)



