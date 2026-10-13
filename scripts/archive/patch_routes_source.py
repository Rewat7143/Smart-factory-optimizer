import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

pattern = r'if telemetry\.latest_reading:\n\s*state\["live_status"\] = "CONNECTED"'
replacement = """if telemetry.latest_reading:
        # Check explicit data source
        source_val = telemetry.latest_reading.data_source.value
        if source_val == "SIMULATED_RASPI":
            state["live_status"] = "CONNECTED_TEST"
            state["data_source"] = "SIMULATED_RASPI"
        else:
            state["live_status"] = "CONNECTED"
            state["data_source"] = source_val"""

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
