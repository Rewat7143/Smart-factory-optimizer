import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
@router.post("/optimize")
def run_optimization(mode: str = "SIMULATION"):
    # END-TO-END INTELLIGENCE PIPELINE
    # 1. FACTORY STATE
    state = _get_factory_state(mode)
    current_power = state.get("current_demand_kw", 0.0)
    
    # 2. FORECAST
    predicted_peak = current_power * 1.1 # Default fallback if no forecast
    forecasts = state.get("forecast", [])
    if forecasts:
        predicted_peak = forecasts[0].get("predicted_kw", predicted_peak)
        
    safe_target = factory.safe_operating_target_kw
"""

pattern = r'@router\.post\("/optimize"\)\s*def run_optimization\(\):.*?safe_target = factory\.safe_operating_target_kw'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
