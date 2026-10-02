import pytest
from datetime import datetime, timezone
from simulator.factory import FactoryModel, FactoryScenario
from ml.forecasting.model import forecaster
from ml.opportunities import opportunity_engine
from optimizer.scheduler import optimize_schedule

def test_end_to_end_peak_event():
    # 1. Generate factory state
    factory = FactoryModel()
    factory.start_demo_production()
    
    # 2. Trigger overlapping loads
    factory.set_scenario(FactoryScenario.PEAK_RISK)
    factory.update(1.0)
    
    current_power = factory.get_total_power_kw()
    
    # 3. Forecast peak
    # Simple mock forecast for test
    predicted_peak = current_power * 1.2
    
    # 4. Identify contributors (Attribution)
    flexible_loads = []
    critical_loads = []
    
    for a in factory.assets.values():
        if a.status.value in ["RUNNING", "STARTING"]:
            if a.production_dependency:
                critical_loads.append(a.to_dict())
            elif a.criticality == "FLEXIBLE":
                flexible_loads.append({"asset_id": a.asset_id, "name": a.name, "power_kw": a.get_current_power()})
                
    # 5. Run optimizer
    opt_result = optimize_schedule(
        current_demand=current_power,
        predicted_peak=predicted_peak,
        safe_target=factory.safe_operating_target_kw,
        flexible_loads=flexible_loads,
        critical_loads=critical_loads,
        production_target_percent=100.0,
        current_production_percent=100.0
    )
    
    # 6. Reject unsafe option & Select feasible option
    assert opt_result["status"] == "OPTIMIZED"
    
    alts = opt_result["alternatives"]
    rejected = next((a for a in alts if a["status"] == "REJECTED"), None)
    selected = next((a for a in alts if a["status"] == "SELECTED"), None)
    
    assert rejected is not None, "Optimizer must evaluate and reject an unsafe option."
    assert selected is not None, "Optimizer must select a safe option."
    
    # 7. Calculate impact (Assertion)
    assert opt_result["after_peak"] < predicted_peak
    assert opt_result["production_impact"] == "0%"
