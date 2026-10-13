import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
def _get_factory_state(mode: str = "SIMULATION"):
    from simulator.factory import factory, history_db
    from api import telemetry
    import datetime
    
    state = {
        "factory_id": "fac_001",
        "live_status": "OFFLINE",
        "current_demand_kw": 0.0,
        "contract_demand_kw": 100.0,
        "assets": [],
        "history": [],
        "forecast": []
    }
    
    if mode == "SIMULATION":
        sim_state = factory.to_dict()
        state.update(sim_state)
        state["live_status"] = "SIMULATION"
        state["data_source"] = "SIMULATOR"
        state["history"] = []
        state["forecast"] = []
        
        if history_db.history_df is not None and not history_db.history_df.empty:
            df = history_db.history_df.copy()
            df = df.rename(columns={'total_demand_kw': 'power_kw'})
            df_hist = df[['timestamp', 'power_kw']]
            
            # Send latest ~60 history points to UI
            for _, row in df.tail(60).iterrows():
                state["history"].append({
                    "timestamp": row["timestamp"].isoformat(),
                    "power_kw": row["power_kw"]
                })
                
            try:
                from ml.forecasting.model import forecaster
                # Genuine inference from simulator history
                pred = forecaster.predict_15m_from_history(df_hist)
                if isinstance(pred, dict) and 'predicted_kw' in pred:
                    state["forecast"] = [pred] # Just add the single 15-m forecast step returned
                elif isinstance(pred, list):
                    state["forecast"] = pred
            except Exception as e:
                pass 
                
        return state

    # LIVE MODE - STRICT ISOLATION
    if telemetry.latest_reading:
        source_val = telemetry.latest_reading.data_source.value
        if source_val == "SIMULATED_RASPI":
            state["live_status"] = "CONNECTED_TEST"
            state["data_source"] = "SIMULATED_RASPI"
        else:
            state["live_status"] = "CONNECTED"
            state["data_source"] = source_val
        state["current_demand_kw"] = telemetry.latest_reading.active_power_kw
        
        for r in telemetry.recent_readings_cache:
            state["history"].append({
                "timestamp": r.timestamp.isoformat(),
                "power_kw": r.active_power_kw
            })
            
        if len(telemetry.recent_readings_cache) > 2:
            try:
                from ml.forecasting.model import forecaster
                import pandas as pd
                hist_data = [{"timestamp": r.timestamp, "power_kw": r.active_power_kw} for r in telemetry.recent_readings_cache]
                df_hist = pd.DataFrame(hist_data)
                
                pred = forecaster.predict_15m_from_history(df_hist)
                if isinstance(pred, dict) and 'predicted_kw' in pred:
                    state["forecast"] = [pred]
                elif isinstance(pred, list):
                    state["forecast"] = pred
            except Exception as e:
                pass
                
    return state
"""

pattern = r'def _get_factory_state\(mode: str = "SIMULATION"\):.*?return state'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
