import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
        state["live_status"] = "SIMULATION"
        state["data_source"] = "SIMULATOR"
        state["submetering_available"] = True
"""

pattern = r'\s*state\["live_status"\] = "SIMULATION"\s*state\["data_source"\] = "SIMULATOR"'
content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
