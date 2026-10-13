import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
    # Safety Interlock - Allow evaluation in SIMULATION mode but prohibit physical control
    if mode == "SIMULATION":
        opt_result['status'] = 'SIMULATION_RECOMMENDATION'
        opt_result['message'] = 'Simulation mode: Control recommendations generated but physical execution is disabled.'
    elif not is_live_hardware:
        opt_result['status'] = 'SAFETY_INTERLOCK_ENGAGED'
        opt_result['message'] = 'Optimization and control actions require fresh hardware telemetry.'
        opt_result['actions'] = []
"""

pattern = r'\s*# Safety Interlock\s*if not is_live_hardware:\s*opt_result\[\'status\'\] = \'SAFETY_INTERLOCK_ENGAGED\'\s*opt_result\[\'message\'\] = \'Optimization and control actions require fresh hardware telemetry. Currently using \' \+ source_status\.get\(\'active_source\', \'NONE\'\) \+ \'\.\'\s*opt_result\[\'actions\'\] = \[\]'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
