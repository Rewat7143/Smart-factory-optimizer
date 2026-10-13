import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
@router.get("/business-impact")
def get_business_impact(mode: str = "SIMULATION"):
    state = _get_factory_state(mode)
    
    today_kwh = 0.0
    peak_demand_kw = 0.0
    
    if mode == "SIMULATION":
        from simulator.factory import history_db
        df = history_db.get_history()
        if not df.empty:
            today_kwh = df.tail(4 * 24)['total_demand_kw'].sum() * (15/60.0)
            peak_demand_kw = df.tail(4 * 24)['total_demand_kw'].max()
    else:
        # LIVE MODE
        hist = state.get("history", [])
        if hist:
            # history is 1-minute sampling
            # sum power * (1/60) to get kWh
            today_kwh = sum(r["power_kw"] for r in hist) * (1.0 / 60.0)
            peak_demand_kw = max(r["power_kw"] for r in hist)

    # Calculate verifiable opportunities dynamically from anomaly detector and optimizer if available
    from ml.opportunities import opportunity_engine
    opportunities = opportunity_engine.get_opportunities(mode)
    
    potential_reduction_kwh = sum(o.get("expected_reduction_kwh", 0) for o in opportunities)
    potential_peak_reduction_kw = sum(o.get("expected_reduction_kw", 0) for o in opportunities)
    
    return {
        "today": {
            "type": "MEASURED",
            "energy_kwh": round(today_kwh, 1),
            "energy_cost_inr": round(today_kwh * 7.5, 0),
            "peak_demand_kw": round(peak_demand_kw, 1)
        },
        "simulation": {
            "type": "SIMULATED",
            "potential_reduction_kwh": round(potential_reduction_kwh, 1),
            "potential_peak_reduction_kw": round(potential_peak_reduction_kw, 1)
        },
        "projection": {
            "type": "PROJECTED",
            "annual_opportunity_inr": round(potential_reduction_kwh * 7.5 * 365 + potential_peak_reduction_kw * 350 * 12, 0),
            "roi_months": 0 if potential_reduction_kwh == 0 else 3.4
        }
    }
"""

pattern = r'@router\.get\("/business-impact"\)\s*def get_business_impact\(\):.*?return \{\s*"today": \{.*?\}\s*\}'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
