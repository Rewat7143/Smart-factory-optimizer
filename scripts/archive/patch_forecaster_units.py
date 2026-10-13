import re

file_path = 'backend/ml/forecasting/model.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """        # 4. Construct Features for t_pred
        # The model was trained on 'Usage_kWh' (energy per 15 mins). 
        # Live telemetry is 'power_kw'. We must convert power (kW) to energy (kWh) over 0.25h.
        lag_1h_kwh = resampled_df.loc[t_lag1h, 'mean'] / 4.0
        lag_24h_kwh = resampled_df.loc[t_lag24h, 'mean'] / 4.0
        rolling_mean_4h_kwh = rolling_window['mean'].mean() / 4.0
        
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
            'lag_1h': lag_1h_kwh,
            'lag_24h': lag_24h_kwh,
            'rolling_mean_4h': rolling_mean_4h_kwh
        }])
        
        pred_kwh = self.model.predict(X)[0]
        
        # Convert predicted energy (kWh per 15m) back to average power (kW)
        pred_kw = float(pred_kwh) * 4.0
        
        return {
            'timestamp': t_pred.isoformat(),
            'predicted_kw': pred_kw
        }"""

pattern = r'        # 4\. Construct Features for t_pred.*\'predicted_kw\': float\(pred\)\s*\}'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
