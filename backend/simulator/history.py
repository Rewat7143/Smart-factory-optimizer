import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

class HistoryGenerator:
    """Generates realistic historical data for the factory based on asset characteristics."""
    def __init__(self, factory_model, days: int = 30, interval_min: int = 15):
        self.factory = factory_model
        self.days = days
        self.interval_min = interval_min
        self.history_df = None
        
    def generate(self) -> pd.DataFrame:
        print("Generating realistic historical data...")
        end_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        start_time = end_time - timedelta(days=self.days)
        
        timestamps = pd.date_range(start=start_time, end=end_time, freq=f'{self.interval_min}min')
        n_samples = len(timestamps)
        
        data = {
            'timestamp': timestamps,
            'temperature_c': np.random.normal(25, 5, n_samples) + np.sin(np.linspace(0, self.days * 2 * np.pi, n_samples)) * 5,
            'production_target_percent': np.ones(n_samples) * 100.0,
        }
        
        # Introduce weekends / off shifts
        hour_of_day = timestamps.hour
        day_of_week = timestamps.dayofweek
        
        # 0 = Monday, 6 = Sunday
        # Let's say Sunday is off
        is_operating = (day_of_week < 6) & (hour_of_day >= 6) & (hour_of_day < 22)
        
        data['production_rate'] = np.where(is_operating, np.random.uniform(90, 100, n_samples), 0.0)
        
        # Base demand from production assets
        total_demand = np.zeros(n_samples)
        
        for asset_id, asset in self.factory.assets.items():
            # Asset specific power curve
            asset_power = np.zeros(n_samples)
            if asset.production_dependency:
                asset_power = np.where(data['production_rate'] > 0, 
                                     asset.operating_power_kw * (data['production_rate'] / 100.0) + np.random.normal(0, 0.5, n_samples), 
                                     asset.idle_power_kw)
            elif asset.category == 'HVAC':
                # HVAC depends on temperature and operation
                asset_power = np.where(is_operating, 
                                     asset.operating_power_kw + (data['temperature_c'] - 20) * 0.5, 
                                     asset.idle_power_kw)
            else:
                # Flexible loads
                # Random cycles during operation
                cycles = np.random.choice([0, asset.operating_power_kw], p=[0.3, 0.7], size=n_samples)
                asset_power = np.where(is_operating, cycles, asset.idle_power_kw)
                
            # Bound the power to >= 0
            asset_power = np.maximum(asset_power, 0)
            data[f'{asset_id}_power'] = asset_power
            total_demand += asset_power
            
        data['total_demand_kw'] = total_demand
        
        self.history_df = pd.DataFrame(data)
        
        # Fill NA just in case
        self.history_df.fillna(0, inplace=True)
        return self.history_df
        
    def get_history(self) -> pd.DataFrame:
        if self.history_df is None:
            self.generate()
        return self.history_df
