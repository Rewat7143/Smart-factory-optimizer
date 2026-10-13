with open('backend/api/telemetry.py', 'r') as f:
    content = f.read()

new_endpoint = """
from pydantic import BaseModel
class CustomHistoryPayload(BaseModel):
    history: list

@router.post("/forecast/custom")
def run_custom_forecast(payload: CustomHistoryPayload):
    from ml.forecasting.model import forecaster
    import pandas as pd
    
    if not payload.history:
        return {"forecast": None, "error": "No history provided"}
        
    try:
        hist_data = [{"timestamp": r.get('timestamp'), "power_kw": r.get('active_power_kw')} for r in payload.history]
        df_hist = pd.DataFrame(hist_data)
        
        pred = forecaster.predict_15m_from_history(df_hist)
        return {"forecast": pred}
    except Exception as e:
        return {"forecast": None, "error": str(e)}

"""

if '/forecast/custom' not in content:
    content += new_endpoint
    with open('backend/api/telemetry.py', 'w') as f:
        f.write(content)
