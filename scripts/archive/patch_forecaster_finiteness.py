import re

file_path = 'backend/ml/forecasting/model.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """        pred_kwh = self.model.predict(X)[0]
        
        # Convert predicted energy (kWh per 15m) back to average power (kW)
        pred_kw = float(pred_kwh) * 4.0
        
        if pd.isna(pred_kw) or np.isinf(pred_kw):
            raise Exception("Forecast failed: Model returned non-finite value")
            
        if pred_kw < 0:
            raise Exception(f"Forecast failed: Model returned negative power ({pred_kw} kW)")
        
        return {"""

pattern = r'        pred_kwh = self\.model\.predict\(X\)\[0\]\n\s*# Convert predicted energy \(kWh per 15m\) back to average power \(kW\)\n\s*pred_kw = float\(pred_kwh\) \* 4\.0\n\s*return \{'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
