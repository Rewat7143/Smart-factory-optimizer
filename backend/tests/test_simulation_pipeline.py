import pytest
from simulator.factory import factory, FactoryScenario
from api.routes import _get_factory_state, run_optimization, get_anomalies


def test_simulation_pipeline_end_to_end():
    factory.start_demo_production()
    
    # Turn off flexible loads to ensure Normal Production is < 90kW
    from simulator.machines import MachineState
    for asset_id in ["CMP-001", "PMP-001", "HVAC-001", "AUX-001"]:
        a = factory.get_asset(asset_id)
        if a: a.status = MachineState.OFF

    factory.sim_time_minutes = 0.0

    
    # 1. Normal Production
    for _ in range(10): factory.update(1.0)
    assert factory.active_scenario == FactoryScenario.NORMAL_PRODUCTION, "Scenario should be NORMAL_PRODUCTION"
    state = _get_factory_state("SIMULATION")
    assert state['current_demand_kw'] > 0, "Demand should be positive"
    assert state['current_demand_kw'] <= 90.0, f"Demand {state['current_demand_kw']} should be <= safe target (90)"
    
    # 2. Gradual Increase (15-25m)
    for _ in range(10): factory.update(1.0)
    assert factory.active_scenario == FactoryScenario.HIGH_PRODUCTION, "Scenario should be HIGH_PRODUCTION"
    state2 = _get_factory_state("SIMULATION")
    assert state2['current_demand_kw'] > state['current_demand_kw'], "Demand should increase due to HVAC"
    
    # 3. Peak Overlap (35-40m)
    for _ in range(18): factory.update(1.0)
    assert factory.active_scenario == FactoryScenario.PEAK_RISK, "Scenario should be PEAK_RISK"
    state3 = _get_factory_state("SIMULATION")
    assert state3['current_demand_kw'] > 90.0, "Demand should exceed 90.0 kW during overlap"
    
    # Optimizer should trigger and protect critical loads
    opt = run_optimization("SIMULATION")
    assert opt['pipeline']['peak_risk'] == "HIGH", "Peak risk should be HIGH"
    # Ensure critical loads are NOT in the shed list
    shed_actions = opt.get('optimization', {}).get('actions', [])
    assert len(shed_actions) > 0, "Should suggest shed actions"
    for action in shed_actions:
        assert not action.get('production_dependency', False), f"Optimizer suggested shedding critical load {action['asset']}!"
    
    # 4. Machine Anomaly (40-45m)
    for _ in range(4): factory.update(1.0)
    assert factory.active_scenario == FactoryScenario.MACHINE_ANOMALY, "Scenario should be MACHINE_ANOMALY"
    anomalies = get_anomalies()
    assert len(anomalies) > 0, "Should detect anomaly"
    assert any(a['type'] == 'UNEXPECTED_POWER' for a in anomalies), "Should detect UNEXPECTED_POWER"
    
    # 5. Recovery (50-60m)
    for _ in range(10): factory.update(1.0)
    assert factory.active_scenario == FactoryScenario.NORMAL_PRODUCTION, "Scenario should recover to NORMAL_PRODUCTION"
    state_rec = _get_factory_state("SIMULATION")
    assert state_rec['current_demand_kw'] < 90.0, "Demand should recover below safe target"
    
