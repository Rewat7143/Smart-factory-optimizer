import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
def _get_factory_state(mode: str = "SIMULATION"):
    from simulator.factory import factory, history_db
    from api import telemetry
    import datetime
    
    if mode == "SIMULATION":
        state = factory.to_dict()
        state["live_status"] = "SIMULATION"
        state["data_source"] = "SIMULATOR"
        state["history"] = []
        state["forecast"] = []
        
        # Populate history from simulator history_db
        if history_db.history_df is not None and not history_db.history_df.empty:
            df = history_db.history_df.tail(60) # last 60 readings
            for _, row in df.iterrows():
                state["history"].append({
                    "timestamp": row["timestamp"].isoformat(),
                    "power_kw": row["total_demand_kw"]
                })
                
            try:
                from ml.forecasting.model import forecaster
                # Use actual forecaster with simulated history
                pred_kw = forecaster.predict_15m(state["current_demand_kw"], state["current_demand_kw"], factory.current_production_percent, factory.temperature_c)
                last_ts = df.iloc[-1]["timestamp"]
                for i in range(1, 5):
                    state["forecast"].append({
                        "timestamp": (last_ts + datetime.timedelta(minutes=15*i)).isoformat(),
                        "predicted_kw": pred_kw
                    })
            except Exception as e:
                pass # If model fails, forecast remains empty (honesty constraint)
                
        return state
"""

pattern = r'def _get_factory_state\(mode: str = "SIMULATION"\):.*?(?=\s*# LIVE MODE - STRICT ISOLATION)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
