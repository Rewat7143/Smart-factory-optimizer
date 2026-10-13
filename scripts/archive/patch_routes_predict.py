import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

pattern = r'try:\n\s*from ml\.forecasting\.model import forecaster.*?pred = forecaster\.predict_15m\(base_power, lag_power, 85\.0, 30\.0\)'

replacement = """try:
                from ml.forecasting.model import forecaster
                import pandas as pd
                # Build history dataframe
                hist_data = [{"timestamp": r.timestamp, "power_kw": r.active_power_kw} for r in telemetry.recent_readings_cache]
                df_hist = pd.DataFrame(hist_data)
                
                pred = forecaster.predict_15m_from_history(df_hist)"""
                
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
