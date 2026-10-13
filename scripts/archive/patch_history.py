import re

file_path = 'backend/simulator/history.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """    def get_history(self) -> pd.DataFrame:
        if self.history_df is None:
            self.generate()
        return self.history_df

    def append_reading(self, timestamp, power_kw, production_percent):
        if self.history_df is not None:
            new_row = pd.DataFrame({
                'timestamp': [pd.to_datetime(timestamp)],
                'total_demand_kw': [power_kw],
                'production_percent': [production_percent],
                'temperature_c': [self.factory.temperature_c]
            })
            self.history_df = pd.concat([self.history_df, new_row], ignore_index=True)
"""

pattern = r'\s*def get_history\(self\) -> pd\.DataFrame:.*?return self\.history_df'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
