import re
file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

pattern = r'pred_ts = last_ts \+ datetime\.timedelta\(minutes=15\)\s*state\["forecast"\]\.append\(\{\s*"timestamp": pred_ts\.isoformat\(\),\s*"predicted_kw": pred\s*\}\)'

replacement = """state["forecast"].append(pred)"""

content = re.sub(pattern, replacement, content, flags=re.DOTALL)
with open(file_path, 'w') as f:
    f.write(content)
