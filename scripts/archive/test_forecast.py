import sys
import os
import pandas as pd
import datetime
# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/backend')

from backend.simulator.factory import history_db
from backend.api.routes import _get_factory_state

state = _get_factory_state("SIMULATION")
print("Forecast length:", len(state.get("forecast", [])))
if not state.get("forecast"):
    # Try calling model directly to see why it fails
    from backend.ml.forecasting.model import forecaster
    df = history_db.history_df.copy()
    df = df.rename(columns={'total_demand_kw': 'power_kw'})
    df_hist = df[['timestamp', 'power_kw']]
    try:
        pred = forecaster.predict_15m_from_history(df_hist)
        print("Model output directly:", pred)
    except Exception as e:
        print("Model error directly:", e)
