import re

file_path = 'backend/ml/forecasting/model.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """    def predict_15m_from_history(self, history_df: pd.DataFrame) -> float:
        # history_df must have 'timestamp' and 'power_kw'
        if self.model is None:
            if not self.load():
                raise Exception("Model not loaded - cannot provide genuine forecast")
                
        if len(history_df) == 0:
            raise Exception("No history provided")
            
        # Ensure timestamp is datetime and sort
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'], utc=True)
        history_df = history_df.sort_values('timestamp')
        
        # 1. Resample to 15-minute intervals as used in training
        history_df = history_df.set_index('timestamp')
        resampled_df = history_df.resample('15min').mean().interpolate(method='linear')
        
        if len(resampled_df) == 0:
            raise Exception("No valid data after resampling to 15-minute intervals")
            
        now = resampled_df.index[-1]
        time_span = now - resampled_df.index[0]
        
        # 2. Enforce the exact history length required by the model features (24 hours = 96 periods of 15min)
        if time_span < pd.Timedelta(hours=24):
            raise Exception(f"Insufficient history: Model requires at least 24 hours of data for 24h lag features, but got {time_span}")
            
        # 3. Calculate exact features used in training using the resampled data
        current_demand = resampled_df['power_kw'].iloc[-1]
        
        # lag_1h is shift(4) in 15-min data
        if len(resampled_df) >= 5:
            lag_1h = resampled_df['power_kw'].iloc[-5]
        else:
            raise Exception("Missing data for 1h lag")
            
        # lag_24h is shift(96) in 15-min data
        if len(resampled_df) >= 97:
            lag_24h = resampled_df['power_kw'].iloc[-97]
        else:
            raise Exception("Missing data for 24h lag")
            
        # rolling_mean_4h is rolling(16) in 15-min data, shifted by 1
        if len(resampled_df) >= 17:
            rolling_mean_4h = resampled_df['power_kw'].iloc[-17:-1].mean()
        else:
            raise Exception("Missing data for 4h rolling mean")
            
        h = now.hour
        m = now.minute
        dow = now.weekday()
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
        return float(pred)"""

# Replacing the method logic
pattern = r'    def predict_15m_from_history\(self, history_df: pd\.DataFrame\) -> float:.*return float\(pred\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
