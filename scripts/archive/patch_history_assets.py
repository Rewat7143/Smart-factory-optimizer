import re

file_path = 'backend/simulator/history.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
    def append_reading(self, timestamp, power_kw, production_percent):
        if self.history_df is not None:
            new_data = {
                'timestamp': [pd.to_datetime(timestamp)],
                'total_demand_kw': [power_kw],
                'production_percent': [production_percent],
                'temperature_c': [self.factory.temperature_c]
            }
            # Append individual asset powers
            for asset_id, asset in self.factory.assets.items():
                new_data[f'{asset_id}_power'] = [asset.get_current_power()]
                
            new_row = pd.DataFrame(new_data)
            self.history_df = pd.concat([self.history_df, new_row], ignore_index=True)
"""

pattern = r'\s*def append_reading.*?self\.history_df = pd\.concat\(\[self\.history_df, new_row\], ignore_index=True\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
