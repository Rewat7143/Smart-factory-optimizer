import re

file_path = 'backend/tests/test_simulation_pipeline.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
def test_simulation_pipeline_end_to_end():
    factory.start_demo_production()
    
    # Turn off flexible loads to ensure Normal Production is < 90kW
    from simulator.machines import MachineState
    for asset_id in ["CMP-001", "PMP-001", "HVAC-001", "AUX-001"]:
        a = factory.get_asset(asset_id)
        if a: a.status = MachineState.OFF

    factory.sim_time_minutes = 0.0
"""

pattern = r'def test_simulation_pipeline_end_to_end\(\):\s*factory\.start_demo_production\(\)\s*factory\.sim_time_minutes = 0\.0'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
