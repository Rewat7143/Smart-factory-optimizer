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
    forecasts = state.get("forecast", [])
    forecast_status = "AVAILABLE" if forecasts else "FORECAST_UNAVAILABLE"
    
    if forecasts:
        predicted_peak = forecasts[0].get("predicted_kw", current_power)
    else:
        # Safe conservative fallback without fabricated ML heuristics
        predicted_peak = current_power
        
    safe_target = factory.safe_operating_target_kw

    # 3. PEAK RISK
    peak_risk = "HIGH" if predicted_peak > safe_target else "LOW"
"""

pattern = r'@router\.post\("/optimize"\)\s*def run_optimization.*?peak_risk = "HIGH" if predicted_peak > safe_target else "LOW"'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Add forecast_status to the return payload
replacement2 = """
    return {
        "pipeline": {
            "current_demand": round(current_power, 1),
            "predicted_peak": round(predicted_peak, 1),
            "forecast_status": forecast_status,
            "safe_target": safe_target,
"""
pattern2 = r'return \{\s*"pipeline": \{\s*"current_demand": round\(current_power, 1\),\s*"predicted_peak": round\(predicted_peak, 1\),\s*"safe_target": safe_target,'
content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
