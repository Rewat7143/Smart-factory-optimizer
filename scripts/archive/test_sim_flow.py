import sys
import os
import datetime
# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/backend')

from backend.simulator.factory import factory, history_db
from backend.api.routes import _get_factory_state
from backend.ml.forecasting.model import forecaster

print("Initial active scenario:", factory.active_scenario)

# Advance 20 minutes (20 updates of 1.0 minutes)
for i in range(20):
    factory.update(1.0)
    
print("After 20m scenario:", factory.active_scenario)
print("Current sim_time_minutes:", factory.sim_time_minutes)
print("History length:", len(history_db.history_df) if history_db.history_df is not None else 0)

# Check forecast inference
state = _get_factory_state("SIMULATION")
print("Forecast length:", len(state.get("forecast", [])))
if len(state.get("forecast", [])) > 0:
    print("Forecast output:", state["forecast"])
else:
    print("No forecast output")
