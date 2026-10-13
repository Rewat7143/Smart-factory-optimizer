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
            
        # 1. Clean timestamps and drop duplicates/stale data
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'], utc=True)
        history_df = history_df.dropna(subset=['timestamp', 'power_kw'])
        history_df = history_df.drop_duplicates(subset=['timestamp'])
        history_df = history_df.sort_values('timestamp')
        
        # 2. Resample to strict 15-minute intervals (mean aggregation and count, NO blind interpolation)
        history_df = history_df.set_index('timestamp')
        # We need both mean and count to validate bin density
        resampled_df = history_df['power_kw'].resample('15min').agg(['mean', 'count'])
        
        if len(resampled_df) == 0:
            raise Exception("No valid data after resampling to 15-minute intervals")
            
        now = resampled_df.index[-1]
        
        # Calculate time span and check for sufficient history
        time_span = now - resampled_df.index[0]
        if time_span < pd.Timedelta(hours=24):
            raise Exception(f"Insufficient history: Model requires 24h of data. Got {time_span}")
            
        # Define minimum acceptable readings per 15-min bin.
        # If the polling frequency is 1 second, a perfect bin has 900 readings.
        # We enforce at least 5% coverage (45 readings) to consider a bin statistically representative,
        # avoiding a bin being validated merely because its mean is non-null from a single stray reading.
        MIN_BIN_COUNT = 45
        
        # 3. Check for unacceptable missing data gaps for required lags
        t_pred = now + pd.Timedelta(minutes=15)
        
        t_lag1h = t_pred - pd.Timedelta(hours=1)
        t_lag24h = t_pred - pd.Timedelta(hours=24)
        
        # Check if exactly required lags are present in the dataset AND have sufficient density
        if t_lag1h not in resampled_df.index or pd.isna(resampled_df.loc[t_lag1h, 'mean']):
            raise Exception(f"Missing required data for lag_1h at {t_lag1h}")
        if resampled_df.loc[t_lag1h, 'count'] < MIN_BIN_COUNT:
            raise Exception(f"Inadequate sampling for lag_1h at {t_lag1h} (Count: {resampled_df.loc[t_lag1h, 'count']} < {MIN_BIN_COUNT})")
            
        if t_lag24h not in resampled_df.index or pd.isna(resampled_df.loc[t_lag24h, 'mean']):
            raise Exception(f"Missing required data for lag_24h at {t_lag24h}")
        if resampled_df.loc[t_lag24h, 'count'] < MIN_BIN_COUNT:
            raise Exception(f"Inadequate sampling for lag_24h at {t_lag24h} (Count: {resampled_df.loc[t_lag24h, 'count']} < {MIN_BIN_COUNT})")
            
        # Get the rolling 4h window ending at `now` (which is t_pred - 15m)
        t_rolling_start = now - pd.Timedelta(hours=4) + pd.Timedelta(minutes=15) # 16 steps total
        rolling_window = resampled_df.loc[t_rolling_start:now]
        
        if len(rolling_window) < 16 or rolling_window['mean'].isna().sum() > 2:
            raise Exception(f"Insufficient data in rolling 4h window. Found {len(rolling_window)} steps, {rolling_window['mean'].isna().sum()} missing.")
            
        # 4. Construct Features for t_pred
        lag_1h = resampled_df.loc[t_lag1h, 'mean']
        lag_24h = resampled_df.loc[t_lag24h, 'mean']
        rolling_mean_4h = rolling_window['mean'].mean() # Will handle up to 2 missing values gracefully
        
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

pattern = r'    def predict_15m_from_history\(self, history_df: pd\.DataFrame\) -> dict:.*return \{\s*\'timestamp\': t_pred\.isoformat\(\),\s*\'predicted_kw\': float\(pred\)\s*\}'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
