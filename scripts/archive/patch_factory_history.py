import re

file_path = 'backend/simulator/factory.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
        # Push to history
        global history_db
        from datetime import datetime, timezone
        if 'history_db' in globals() and history_db.history_df is not None:
            history_db.append_reading(datetime.now(timezone.utc), power, self.current_production_percent)
"""

pattern = r'\s*# Push to history.*?history_db\.append_reading\(datetime\.now\(timezone\.utc\), power, self\.current_production_percent\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
