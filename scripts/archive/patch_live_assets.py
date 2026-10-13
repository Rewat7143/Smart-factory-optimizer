import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
    # LIVE MODE - STRICT ISOLATION
    state["submetering_available"] = False
    
    # Populate asset inventory but indicate lack of measurements
    for asset in factory.assets.values():
        asset_dict = asset.to_dict()
        asset_dict["power_kw"] = None
        asset_dict["status"] = "UNKNOWN"
        state["assets"].append(asset_dict)
        
    if telemetry.latest_reading:
"""

pattern = r'\s*# LIVE MODE - STRICT ISOLATION\n\s*if telemetry\.latest_reading:'
content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
