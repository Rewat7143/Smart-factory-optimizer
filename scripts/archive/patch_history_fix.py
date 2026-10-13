import re

file_path = 'backend/simulator/history.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
        return self.history_df

    def get_history(self) -> pd.DataFrame:
"""

pattern = r'return self\.history_df\s*def get_history\(self\) -> pd\.DataFrame:'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
