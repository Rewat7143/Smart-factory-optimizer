import re

file_path = 'backend/simulator/factory.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
        # Accumulate energy
        power = self.get_total_power_kw()
        self.total_energy_kwh += power * (dt_minutes / 60.0)
        
        # Push to history
        from simulator.history import history_db
        from datetime import datetime, timezone
        if history_db.history_df is not None:
            history_db.append_reading(datetime.now(timezone.utc), power, self.current_production_percent)
"""

pattern = r'\s*# Accumulate energy\s*power = self\.get_total_power_kw\(\)\s*self\.total_energy_kwh \+= power \* \(dt_minutes / 60\.0\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
