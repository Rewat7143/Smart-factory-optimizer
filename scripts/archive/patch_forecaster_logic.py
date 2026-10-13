import re

file_path = 'backend/ml/forecasting/model.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """    def predict_15m_from_history(self, history_df: pd.DataFrame) -> dict:
        # Returns a dict with {'timestamp': str, 'predicted_kw': float}
        if self.model is None:
            if not self.load():
                raise Exception("Model not loaded - cannot provide genuine forecast")
                
        if len(history_df) == 0:
            raise Exception("No history provided")
            
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'], utc=True)
        history_df = history_df.sort_values('timestamp')
        
        # 1. Resample to strict 15-minute intervals (mean aggregation, NO blind interpolation)
        history_df = history_df.set_index('timestamp')
        resampled_df = history_df.resample('15min').mean()
        
        if len(resampled_df) == 0:
            raise Exception("No valid data after resampling to 15-minute intervals")
            
        now = resampled_df.index[-1]
        
        # Calculate time span and check for sufficient history
        time_span = now - resampled_df.index[0]
        if time_span < pd.Timedelta(hours=24):
            raise Exception(f"Insufficient history: Model requires 24h of data. Got {time_span}")
            
        # 2. Check for unacceptable missing data gaps (e.g. more than 10% missing or missing required lags)
        # We need the last 16 readings for rolling_mean, and specific readings for lags.
        # Target prediction time: t_pred = now + 15min
        t_pred = now + pd.Timedelta(minutes=15)
        
        t_lag1h = t_pred - pd.Timedelta(hours=1)
        t_lag24h = t_pred - pd.Timedelta(hours=24)
        
        # Check if exactly required lags are present in the dataset
        if t_lag1h not in resampled_df.index or pd.isna(resampled_df.loc[t_lag1h, 'power_kw']):
            raise Exception(f"Missing required data for lag_1h at {t_lag1h}")
            
        if t_lag24h not in resampled_df.index or pd.isna(resampled_df.loc[t_lag24h, 'power_kw']):
            raise Exception(f"Missing required data for lag_24h at {t_lag24h}")
            
        # Get the rolling 4h window ending at `now` (which is t_pred - 15m)
        t_rolling_start = now - pd.Timedelta(hours=4) + pd.Timedelta(minutes=15) # 16 steps total
        rolling_window = resampled_df.loc[t_rolling_start:now, 'power_kw']
        
        if len(rolling_window) < 16 or rolling_window.isna().sum() > 2:
            raise Exception(f"Insufficient data in rolling 4h window. Found {len(rolling_window)} steps, {rolling_window.isna().sum()} missing.")
            
        # 3. Construct Features for t_pred
        lag_1h = resampled_df.loc[t_lag1h, 'power_kw']
        lag_24h = resampled_df.loc[t_lag24h, 'power_kw']
        rolling_mean_4h = rolling_window.mean() # Will handle up to 2 missing values gracefully via pandas mean()
        
        h = t_pred.hour
        m = t_pred.minute
        dow = t_pred.weekday()
        is_weekend = 1 if dow >= 5 else 0
        nsm = h * 3600 + m * 60
        
        X = pd.DataFrame([{
            'hour': h,
            'minute': m,
            'day_of_week': dow,
            'is_weekend': is_weekend,
            'NSM': nsm,
            'lag_1h': lag_1h,
            'lag_24h': lag_24h,
            'rolling_mean_4h': rolling_mean_4h
        }])
        
        pred = self.model.predict(X)[0]
        
        return {
            'timestamp': t_pred.isoformat(),
            'predicted_kw': float(pred)
        }"""

pattern = r'    def predict_15m_from_history\(self, history_df: pd\.DataFrame\) -> float:.*return float\(pred\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
