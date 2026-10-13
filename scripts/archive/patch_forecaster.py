import re

file_path = 'backend/ml/forecasting/model.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """class DemandForecaster:
    def __init__(self, model_path: str = "models/forecasting/xgboost_steel_v1.joblib"):
        self.model_path = model_path
        self.model = None
        
    def load(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            return True
        return False
        
    def predict_15m_from_history(self, history_df: pd.DataFrame) -> float:
        # history_df should have 'timestamp' and 'power_kw'
        if self.model is None:
            if not self.load():
                raise Exception("Model not loaded - cannot provide genuine forecast")
                
        if len(history_df) == 0:
            raise Exception("No history provided")
            
        # Ensure timestamp is datetime and sort
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'], utc=True)
        history_df = history_df.sort_values('timestamp')
        
        now = history_df['timestamp'].iloc[-1]
        
        # We need at least 1 hour of history to calculate lag_1h.
        time_span = now - history_df['timestamp'].iloc[0]
        if time_span < pd.Timedelta(hours=1):
            raise Exception(f"Insufficient history: Model requires at least 1 hour of data, but got {time_span}")
            
        current_demand = history_df['power_kw'].iloc[-1]
        
        # Calculate lag_1h
        one_hour_ago = now - pd.Timedelta(hours=1)
        # closest reading to one hour ago
        idx_1h = (history_df['timestamp'] - one_hour_ago).abs().idxmin()
        lag_1h = history_df.loc[idx_1h, 'power_kw']
        
        # Calculate lag_24h if possible, otherwise use current
        lag_24h = current_demand
        if time_span >= pd.Timedelta(hours=24):
            twenty_four_hours_ago = now - pd.Timedelta(hours=24)
            idx_24h = (history_df['timestamp'] - twenty_four_hours_ago).abs().idxmin()
            lag_24h = history_df.loc[idx_24h, 'power_kw']
            
        # Calculate rolling_mean_4h if possible, otherwise use available mean
        if time_span >= pd.Timedelta(hours=4):
            four_hours_ago = now - pd.Timedelta(hours=4)
            recent_4h = history_df[history_df['timestamp'] >= four_hours_ago]
            rolling_mean_4h = recent_4h['power_kw'].mean()
        else:
            rolling_mean_4h = history_df['power_kw'].mean()
        
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

# Replacing the class logic
pattern = r'class DemandForecaster:.*return float\(pred\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
