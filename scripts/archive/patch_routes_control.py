import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
    # 7. LOG TO GOOGLE SHEETS
    from api.control import register_peak_event
    
    if current_power > safe_target:
        register_peak_event("MEASURED_PEAK", current_power, safe_target, opt_result.get('actions', []))
    elif predicted_peak > safe_target:
        register_peak_event("PREDICTED_PEAK", predicted_peak, safe_target, opt_result.get('actions', []))

    import uuid
"""

pattern = r'\s*# 7\. LOG TO GOOGLE SHEETS\s*import uuid'
content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
