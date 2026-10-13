import re

file_path = 'backend/ml/forecasting/model.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
        pred_kwh = self.model.predict(X)[0]
        return float(pred_kwh) * 4.0
"""

pattern = r'\s*pred = self\.model\.predict\(X\)\[0\]\s*return float\(pred\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
