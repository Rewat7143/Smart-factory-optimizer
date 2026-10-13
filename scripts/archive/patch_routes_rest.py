import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

# Fix /optimize
pattern_opt = r'@router.post\("/optimize"\)\ndef run_optimization\(\):.*?return payload'
replacement_opt = """@router.post("/optimize")
def run_optimization(mode: str = "SIMULATION"):
    if mode == "LIVE":
        return {
            "status": "UNAVAILABLE",
            "reason": "Asset-level optimization requires asset-level telemetry and explicit equipment constraints. Aggregate meter available only.",
            "pipeline": {
                "peak_risk": "UNKNOWN",
                "predicted_peak": 0,
                "safe_target": 100
            },
            "attribution": [],
            "actions_taken": [],
            "opportunities": []
        }
        
    # END-TO-END INTELLIGENCE PIPELINE
    current_power = factory.get_total_power_kw()
    try:
        from ml.forecasting.model import forecaster
        lag = current_power
        predicted_peak = forecaster.predict_15m(current_power, lag, factory.current_production_percent, factory.temperature_c)
    except:
        predicted_peak = current_power * 1.1
        
    safe_target = factory.safe_operating_target_kw
    peak_risk = "HIGH" if predicted_peak > safe_target else "LOW"
    headroom = safe_target - current_power
    
    flexible_loads = []
    critical_loads = []
    attribution = []
    
    for a in factory.assets.values():
        if a.status.value in ["RUNNING", "STARTING"]:
            contribution = a.get_current_power()
            if a.production_dependency:
                critical_loads.append(a)
            else:
                flexible_loads.append(a)
                
            attribution.append({
                "asset_id": a.asset_id,
                "contribution_kw": round(contribution, 1),
                "is_flexible": not a.production_dependency
            })
            
    attribution.sort(key=lambda x: x["contribution_kw"], reverse=True)
    
    actions = []
    if peak_risk == "HIGH":
        for a in flexible_loads:
            if a.status.value == "RUNNING" and (predicted_peak > safe_target):
                action = a.apply_load_shed(20)
                if action["success"]:
                    actions.append(action)
                    predicted_peak -= action["shed_kw"]
                    
    payload = {
        "status": "SUCCESS",
        "pipeline": {
            "current_power": current_power,
            "predicted_peak": predicted_peak,
            "safe_target": safe_target,
            "headroom": headroom,
            "peak_risk": peak_risk
        },
        "attribution": attribution,
        "actions_taken": actions,
        "opportunities": []
    }
    return payload"""
content = re.sub(pattern_opt, replacement_opt, content, flags=re.DOTALL)


# Fix /maintenance/status
pattern_maint = r'@router.get\("/maintenance/status"\)\ndef get_maintenance_status\(\):.*?return payload'
replacement_maint = """@router.get("/maintenance/status")
def get_maintenance_status(mode: str = "SIMULATION"):
    if mode == "LIVE":
        return {
            "status": "UNAVAILABLE",
            "reason": "Predictive maintenance requires component-specific vibration and temperature sensors. Aggregate facility meter available only.",
            "assets": []
        }
        
    assets = []
    for a in factory.assets.values():
        score = a.health_score
        rul = a.estimated_rul_days
        assets.append({
            "asset_id": a.asset_id,
            "health_score": round(score, 1),
            "rul_days": round(rul, 1),
            "primary_anomaly": a.primary_anomaly,
            "status": a.status.value
        })
        
    payload = {
        "status": "ONLINE",
        "assets": assets
    }
    return payload"""
content = re.sub(pattern_maint, replacement_maint, content, flags=re.DOTALL)


# Fix /copilot/insights
pattern_copilot = r'@router.get\("/copilot/insights"\)\ndef get_copilot_insights\(\):.*?return payload'
replacement_copilot = """@router.get("/copilot/insights")
def get_copilot_insights(mode: str = "SIMULATION"):
    from api import telemetry
    if mode == "LIVE":
        if not telemetry.latest_reading:
            return {
                "status": "OFFLINE",
                "insights": [{
                    "type": "WARNING",
                    "content": "I cannot analyze the factory conditions because no real telemetry is currently available from the meter.",
                    "confidence": 1.0,
                    "actionable": False
                }]
            }
        else:
            return {
                "status": "ONLINE",
                "insights": [{
                    "type": "INFO",
                    "content": f"Live telemetry is active. Current measured load is {telemetry.latest_reading.active_power_kw} kW. Component-level diagnostics are disabled because only an aggregate meter is connected.",
                    "confidence": 1.0,
                    "actionable": False
                }]
            }
            
    payload = {
        "status": "ONLINE",
        "insights": copilot.get_latest_insights(factory)
    }
    return payload"""
content = re.sub(pattern_copilot, replacement_copilot, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

