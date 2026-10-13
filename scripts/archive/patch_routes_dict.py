import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

pattern = r'pred = forecaster\.predict_15m_from_history\(df_hist\)\s*pred_ts = last_ts \+ datetime\.timedelta\(minutes=15\)\s*state\["forecast"\]\.append\(\{\s*"timestamp": pred_ts\.isoformat\(\),\s*"predicted_kw": pred\s*\}\)'

replacement = """pred_result = forecaster.predict_15m_from_history(df_hist)
                state["forecast"].append(pred_result)"""

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
