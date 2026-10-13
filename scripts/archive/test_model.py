import sys
import os
import pandas as pd
from ml.forecasting.model import forecaster
import datetime

print("Testing forecasting model with 1-min sampling...")
if not forecaster.load():
    print("FAILED to load model.")
else:
    print("Model loaded successfully.")
    
    now = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)
    hist_data = []
    for i in range(24 * 60 + 30): # 24.5 hours of 1-minute samples
        ts = now - datetime.timedelta(minutes=(24*60+30)-i)
        hist_data.append({
            "timestamp": ts,
            "power_kw": 80.0 + (i % 10)
        })
    df = pd.DataFrame(hist_data)
    
    try:
        pred = forecaster.predict_15m_from_history(df)
        print("Prediction successful:")
        print(pred)
    except Exception as e:
        print("Prediction failed:", e)
