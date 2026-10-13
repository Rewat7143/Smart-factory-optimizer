import pandas as pd
import datetime
import os
import sys

sys.path.append(os.path.abspath('backend'))
from ml.forecasting.model import DemandForecaster

def generate_history(hours=24.5, missing_index=None, sparse_index=None, interval_seconds=60):
    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now - datetime.timedelta(minutes=15 * 97)
    
    data = []
    # If interval is 60s, there are 15 readings per bin. Expected is 15. MIN_BIN_COUNT = max(3, 15 * 0.25) = 3.
    # To test sparse, we put 1 reading. To test dense, we put 15 readings.
    for i in range(98):
        if i == missing_index:
            continue
            
        readings_in_bin = 1 if i == sparse_index else 15
            
        for r in range(readings_in_bin):
            ts = start_time + datetime.timedelta(minutes=15 * i) + datetime.timedelta(seconds=r * interval_seconds)
            data.append({
                "timestamp": ts,
                "power_kw": 10.0 + (i * 0.1) + (r * 0.001)
            })
    return pd.DataFrame(data)

forecaster = DemandForecaster(model_path="backend/models/forecasting/xgboost_steel_v1.joblib")

def test_long_stream():
    print("\n--- TEST 1: Long Stream (Dense, 60s polling) ---")
    df = generate_history(hours=24.5)
    try:
        res = forecaster.predict_15m_from_history(df)
        print("Success: Prediction returned:", res)
    except Exception as e:
        print("Failed:", e)

def test_missing_lag():
    print("\n--- TEST 2: Missing lag_1h Interval ---")
    # lag_1h is 4 bins ago. For i=97 (now), t_lag1h is i=94.
    df = generate_history(hours=24.5, missing_index=94)
    try:
        res = forecaster.predict_15m_from_history(df)
        print("Failure: Expected exception due to missing lag, but got prediction:", res)
    except Exception as e:
        print("Success: Exception caught:", e)

def test_sparse_interval():
    print("\n--- TEST 3: Insufficient Bin Coverage (Sparse lag_24h) ---")
    # lag_24h is 96 bins ago. For i=97, t_lag24h is i=2.
    df = generate_history(hours=24.5, sparse_index=2)
    try:
        res = forecaster.predict_15m_from_history(df)
        print("Failure: Expected exception due to sparse lag, but got prediction:", res)
    except Exception as e:
        print("Success: Exception caught:", e)

def test_missing_rolling():
    print("\n--- TEST 4: Missing Rolling Window Interval ---")
    # Rolling window is last 16 bins ending at now (i=97), so i=82 to i=97.
    # Missing i=85 breaks the contiguous 16-bin requirement.
    df = generate_history(hours=24.5, missing_index=85)
    try:
        res = forecaster.predict_15m_from_history(df)
        print("Failure: Expected exception due to missing rolling interval, but got prediction:", res)
    except Exception as e:
        print("Success: Exception caught:", e)

if __name__ == "__main__":
    test_long_stream()
    test_missing_lag()
    test_sparse_interval()
    test_missing_rolling()
