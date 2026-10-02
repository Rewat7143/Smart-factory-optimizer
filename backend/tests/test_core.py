import pytest
from datetime import datetime, timezone
from schemas.energy import EnergyReading, DataSource, DataQuality
from simulator.machines import Asset, MachineState, Criticality
from simulator.factory import FactoryModel
from optimizer.scheduler import optimize_schedule

def test_energy_schema():
    reading = EnergyReading(
        timestamp=datetime.now(timezone.utc),
        factory_id="fac_1",
        asset_id="M-001",
        active_power_kw=15.0,
        energy_kwh=0.25,
        machine_state=MachineState.RUNNING,
        data_source=DataSource.SIMULATOR,
        data_quality=DataQuality.GOOD
    )
    assert reading.active_power_kw == 15.0

def test_simulator_and_state():
    factory = FactoryModel()
    factory.update(1.0)
    assert factory.current_production_percent == 0.0
    
    factory.start_demo_production()
    factory.update(1.0)
    # Criticals should be starting/running
    assert factory.current_production_percent > 0

def test_optimizer_production_constraint():
    # If production target is 100% but current is 90%, it must reject
    res = optimize_schedule(
        current_demand=120.0,
        predicted_peak=130.0,
        safe_target=100.0,
        flexible_loads=[{"asset_id": "CMP", "power_kw": 30}],
        critical_loads=[],
        production_target_percent=100.0,
        current_production_percent=90.0
    )
    
    assert res["status"] == "REJECTED"
    assert "violates production constraint" in res["message"]

def test_optimizer_counterfactual():
    # Normal optimization
    res = optimize_schedule(
        current_demand=120.0,
        predicted_peak=130.0,
        safe_target=100.0,
        flexible_loads=[{"asset_id": "CMP", "name": "Compressor", "power_kw": 35.0}],
        critical_loads=[],
        production_target_percent=100.0,
        current_production_percent=100.0
    )
    
    assert res["status"] == "OPTIMIZED"
    assert res["after_peak"] == 95.0
    
    # Check alternatives exist
    alts = res["alternatives"]
    assert len(alts) >= 2
    
    baseline = next(a for a in alts if a["name"] == "BASELINE")
    assert baseline["peak"] == 130.0
    assert baseline["status"] == "CURRENT"
    
    selected = next(a for a in alts if a["status"] == "SELECTED")
    assert selected["peak"] == 95.0
