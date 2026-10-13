def patch_clean(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if "from simulator.factory import history_db" in line:
            start_idx = i - 1
        if "latest_reading = reading" in line:
            end_idx = i
            break
            
    if start_idx != -1 and end_idx != -1:
        # Delete the whole block
        lines[start_idx:end_idx] = []
        
    with open(file_path, 'w') as f:
        f.writelines(lines)

patch_clean('backend/api/telemetry.py')
