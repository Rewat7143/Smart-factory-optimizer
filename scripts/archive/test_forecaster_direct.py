import pandas as pd
import datetime
import os
import sys

sys.path.append(os.path.abspath('backend'))
from ml.forecasting.model import DemandForecaster

def generate_history(hours=24.5, missing_index=None, sparse_index=None):
    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now - datetime.timedelta(minutes=15 * 97)
    
    data = []
    for i in range(98):
        if i == missing_index:
            continue
            
        # Determine how many readings in this bin
        readings_in_bin = 1 if i == sparse_index else 50
            
        for r in range(readings_in_bin):
            ts = start_time + datetime.timedelta(minutes=15 * i) + datetime.timedelta(seconds=r)
            data.append({
                "timestamp": ts,
                "power_kw": 10.0 + (i * 0.1) + (r * 0.001)
            })
    return pd.DataFrame(data)

forecaster = DemandForecaster(model_path="backend/models/forecasting/xgboost_steel_v1.joblib")

def test_long_stream():
    print("\n--- TEST B: Long Stream (24h History, Dense) ---")
    df = generate_history(hours=24.5)
    try:
        res = forecaster.predict_15m_from_history(df)
        print("Success: Prediction returned:", res)
    except Exception as e:
        print("Failed:", e)

def test_missing_interval():
    print("\n--- TEST C: Missing Interval (Drop lag_1h) ---")
    df = generate_history(hours=24.5, missing_index=94)
    try:
        res = forecaster.predict_15m_from_history(df)
        print("Failure: Expected exception due to missing lag, but got prediction:", res)
    except Exception as e:
        print("Success: Forecast unavailable due to missing interval. Exception:", e)

def test_sparse_interval():
    print("\n--- TEST C2: Sparse Interval (Insufficient density for lag_24h) ---")
    # lag_24h is 96 bins ago. For i=97 (now), t_lag24h is i=1 (now - 24h)
    df = generate_history(hours=24.5, sparse_index=2)
    try:
        res = forecaster.predict_15m_from_history(df)
        print("Failure: Expected exception due to sparse lag, but got prediction:", res)
    except Exception as e:
        print("Success: Forecast unavailable due to sparse interval. Exception:", e)

if __name__ == "__main__":
    test_long_stream()
    test_missing_interval()
    test_sparse_interval()
