import re

with open('backend/api/routes.py', 'r') as f:
    content = f.read()

# 1. Update mode dependency
content = content.replace("from fastapi import APIRouter, HTTPException", "from fastapi import APIRouter, HTTPException, Request\nfrom typing import Optional")

# We'll replace the definition of get_factory_state
def_get = """
def _get_factory_state(mode: str = "SIMULATION"):
    from simulator.factory import factory
    from api import telemetry
    
    # Get base simulated state
    state = factory.to_dict()
    
    # If live mode, apply disaggregation override
    if mode == "LIVE":
        if telemetry.latest_reading and (telemetry.latest_reading.active_power_kw > 0):
            live_power = telemetry.latest_reading.active_power_kw
            sim_power = state['current_demand_kw']
            
            # Prevent div by zero
            if sim_power == 0:
                sim_power = 1.0
                
            ratio = live_power / sim_power
            
            state['current_demand_kw'] = live_power
            for asset in state['assets']:
                asset['power_kw'] = asset['power_kw'] * ratio
                
        else:
            # Meter disconnected, zero everything out or special flag
            state['current_demand_kw'] = 0.0
            state['live_status'] = 'OFFLINE'
            for asset in state['assets']:
                asset['power_kw'] = 0.0
                
    return state

@router.get("/factory/state")
def get_factory_state_route(mode: str = "SIMULATION"):
    return _get_factory_state(mode)
"""

# Replace the original def get_factory_state() (which might not have Request)
content = re.sub(r"@router\.get\(\"/factory/state\"\)\ndef get_factory_state\(\).*?return factory\.to_dict\(\)", def_get, content, flags=re.DOTALL)

# Now, any function that was calling `get_factory_state()` internally must call `_get_factory_state(mode)`
content = re.sub(r"state = get_factory_state\(\)", "state = _get_factory_state(mode)", content)

# But wait, we need to add `mode: str = "SIMULATION"` to those endpoints!
endpoints = [
    "@router.get('/maintenance/status')",
    "@router.get('/copilot/insights')",
    "@router.get('/digital-twin/state')",
    "@router.get('/counterfactual/compare')",
    "@router.get('/energy-kpi')",
    "@router.get('/opportunities')",
    "@router.get('/integrity/status')"
]

for ep in endpoints:
    search = ep + "\ndef "
    def_name = content[content.find(search)+len(search):content.find("()", content.find(search))]
    
    content = content.replace(f"{ep}\ndef {def_name}():", f"{ep}\ndef {def_name}(mode: str = 'SIMULATION'):")

with open('backend/api/routes.py', 'w') as f:
    f.write(content)
