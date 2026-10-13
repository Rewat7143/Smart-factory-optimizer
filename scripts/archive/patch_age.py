import re
def patch_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Use regex to find and replace the block
    pattern = re.compile(r'# Determine age\n\s+age = \(datetime\.now\(timezone\.utc\) - latest_reading\.timestamp\)\.total_seconds\(\)\n\s+if age > 15:\n\s+status = "OFFLINE"\n\s+else:\n\s+status = "CONNECTED"', re.MULTILINE)
    
    new_code = """# Determine age based on server receipt time, not device clock
    device_state = live_device_state.get(latest_reading.asset_id)
    if not device_state:
        status = "OFFLINE"
        age = 999
    else:
        age = (datetime.now(timezone.utc) - device_state["last_seen"]).total_seconds()
        if age > 15:
            status = "OFFLINE"
        else:
            status = "CONNECTED" """
            
    if pattern.search(content):
        content = pattern.sub(new_code, content)
        with open(file_path, 'w') as f:
            f.write(content)
        print("Patched age calculation")
    else:
        print("Could not find block to replace")

patch_file('backend/api/telemetry.py')
