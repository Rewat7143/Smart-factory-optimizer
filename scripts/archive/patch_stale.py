import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
    # LIVE MODE - STRICT ISOLATION
    if telemetry.latest_reading:
        from datetime import datetime, timezone
        time_since_last = datetime.now(timezone.utc) - telemetry.latest_reading.timestamp
        is_stale = time_since_last.total_seconds() > 120 # 2 minutes
        
        source_val = telemetry.latest_reading.data_source.value
        
        if is_stale:
            state["live_status"] = "OFFLINE"
            state["data_source"] = source_val
        elif source_val == "SIMULATED_RASPI":
            state["live_status"] = "CONNECTED_TEST"
            state["data_source"] = "SIMULATED_RASPI"
        else:
            state["live_status"] = "CONNECTED"
            state["data_source"] = source_val
            
        state["current_demand_kw"] = telemetry.latest_reading.active_power_kw
"""

pattern = r'\s*# LIVE MODE - STRICT ISOLATION\n\s*if telemetry\.latest_reading:\s*source_val = telemetry\.latest_reading\.data_source\.value\s*if source_val == "SIMULATED_RASPI":\s*state\["live_status"\] = "CONNECTED_TEST"\s*state\["data_source"\] = "SIMULATED_RASPI"\s*else:\s*state\["live_status"\] = "CONNECTED"\s*state\["data_source"\] = source_val\s*state\["current_demand_kw"\] = telemetry\.latest_reading\.active_power_kw'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
