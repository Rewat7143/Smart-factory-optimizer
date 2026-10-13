import sys
import os
from simulator.factory import factory
from api.routes import _get_factory_state, run_optimization
from api.routes import get_anomalies

def test_pipeline():
    print("--- Testing Smart Factory Energy Autopilot Pipeline ---")
    factory.start_demo_production()
    
    # Run loop for 60 iterations (60 simulation minutes)
    for i in range(60):
        factory.update(1.0)
        
        t = factory.sim_time_minutes
        if int(t) == 10:
            print(f"[{int(t)}m] Phase: {factory.active_scenario.value}")
            state = _get_factory_state("SIMULATION")
            print(f"  Demand: {state['current_demand_kw']} kW")
            
        elif int(t) == 38:
            print(f"\n[{int(t)}m] Phase: {factory.active_scenario.value}")
            state = _get_factory_state("SIMULATION")
            print(f"  Demand: {state['current_demand_kw']} kW")
            # Peak warning should trigger, let's call optimize
            opt_res = run_optimization()
            if 'pipeline' in opt_res:
                print(f"  Peak Risk: {opt_res['pipeline'].get('peak_risk')}")
            else:
                print(f"  Peak Risk: Unknown")
                
            if 'optimization' in opt_res and opt_res['optimization'].get('actions'):
                print(f"  Flexible loads suggested for shed: {[a['asset'] for a in opt_res['optimization']['actions']]}")
            else:
                print("  No optimization actions.")
            
        elif int(t) == 42:
            print(f"\n[{int(t)}m] Phase: {factory.active_scenario.value}")
            anomalies = get_anomalies()
            if anomalies:
                for a in anomalies:
                    print(f"  Anomaly detected: Asset {a['asset_id']}, type {a['type']}, severity {a['severity']}")
            else:
                print("  No anomalies detected.")
                
    print("\n--- Pipeline Tests Completed Successfully ---")

if __name__ == "__main__":
    test_pipeline()
