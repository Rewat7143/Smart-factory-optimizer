import re

file_path = 'backend/ml/forecasting/model.py'
with open(file_path, 'r') as f:
    content = f.read()

new_method = """    def predict_15m(self, current_demand: float, lag_demand: float, production_rate: float, temp: float, 
                    lag_4: float = None, lag_8: float = None, rolling_mean: float = None, rolling_max: float = None, hour: int = 12, day_of_week: int = 1) -> float:
        if self.model is None:
            if not self.load():
                return current_demand * 1.05 # Simulator fallback
                
        now = datetime.datetime.now()
        X = pd.DataFrame([{
            'hour': now.hour,
            'minute': now.minute,
            'day_of_week': now.weekday(),
            'is_weekend': 1 if now.weekday() >= 5 else 0,
            'NSM': now.hour * 3600 + now.minute * 60,
            'lag_1h': lag_4 if lag_4 is not None else current_demand,
            'lag_24h': current_demand,
            'rolling_mean_4h': rolling_mean if rolling_mean is not None else current_demand
        }])
        
        pred = self.model.predict(X)[0]
        return float(pred)

    def predict_15m_from_history(self, history_df: pd.DataFrame) -> float:"""

content = content.replace("    def predict_15m_from_history(self, history_df: pd.DataFrame) -> float:", new_method)

with open(file_path, 'w') as f:
    f.write(content)
