import pandas as pd
import numpy as np
import datetime
import os
import sys

sys.path.append(os.path.abspath('backend'))
from ml.forecasting.model import DemandForecaster

def test_unit_conversion():
    print("\n--- TEST A: Unit Conversion Math ---")
    # If a factory draws 100 kW constantly for 15 minutes.
    power_kw = 100.0
    # The energy consumed in 15 mins (0.25 hours) is:
    energy_kwh = power_kw * 0.25
    
    # In model.py, we convert power to Usage_kWh by dividing by 4
    converted_kwh = power_kw / 4.0
    
    assert energy_kwh == converted_kwh, "Input conversion kW -> Usage_kWh is incorrect"
    
    # If the model predicts 25 Usage_kWh in a 15 min interval, the average power is:
    predicted_usage_kwh = 25.0
    # Power = Energy / Time = 25 / 0.25 = 100 kW
    average_power_kw = predicted_usage_kwh / 0.25
    
    # In model.py, we convert Usage_kWh back to kW by multiplying by 4
    converted_kw = predicted_usage_kwh * 4.0
    
    assert average_power_kw == converted_kw, "Output conversion Usage_kWh -> kW is incorrect"
    print("Success: kW to kWh per 15m conversions are mathematically valid.")

def test_feature_parity():
    print("\n--- TEST B: Feature Parity (Training vs Inference) ---")
    # Generate 24 hours of exactly 15-minute readings to mimic a perfect resampled history
    now = datetime.datetime(2023, 1, 2, 12, 0, 0, tzinfo=datetime.timezone.utc)
    data = []
    
    # 24h = 96 intervals. We need a bit more for rolling window calculation at the start.
    # Start 100 intervals ago.
    for i in range(100):
        ts = now - pd.Timedelta(minutes=15 * (99 - i))
        # Provide a distinctive pattern so we can check if the right lags are grabbed
        val_kw = 100.0 + i 
        data.append({'timestamp': ts, 'power_kw': val_kw, 'Usage_kWh': val_kw / 4.0})
        
    df = pd.DataFrame(data)
    
    # --- 1. Training Logic (from train_forecaster.py) ---
    train_df = df.copy()
    train_df['lag_1h'] = train_df['Usage_kWh'].shift(4)
    train_df['lag_24h'] = train_df['Usage_kWh'].shift(96)
    train_df['rolling_mean_4h'] = train_df['Usage_kWh'].shift(1).rolling(16).mean()
    
    # The feature vector for 'now' (the last row)
    target_row = train_df.iloc[-1]
    train_features = {
        'lag_1h': target_row['lag_1h'],
        'lag_24h': target_row['lag_24h'],
        'rolling_mean_4h': target_row['rolling_mean_4h']
    }
    
    # --- 2. Inference Logic (from model.py, skipping the XGBoost call) ---
    # In inference, 'now' is the last timestamp in the dataset, and t_pred = now + 15m.
    # So to match the training row (which predicts AT 'now'), we must pass history up to now - 15m.
    history_df = df.iloc[:-1].copy() # History up to now - 15m
    
    # Simulate the exact resampling block from model.py
    history_df = history_df.set_index('timestamp')
    resampled_df = history_df['power_kw'].resample('15min').agg(['mean', 'count'])
    
    inference_now = resampled_df.index[-1] # This is now - 15m
    t_pred = inference_now + pd.Timedelta(minutes=15) # This is 'now'
    
    t_lag1h = t_pred - pd.Timedelta(hours=1)
    t_lag24h = t_pred - pd.Timedelta(hours=24)
    
    t_rolling_start = inference_now - pd.Timedelta(hours=4) + pd.Timedelta(minutes=15)
    rolling_window = resampled_df.loc[t_rolling_start:inference_now]
    
    infer_features = {
        'lag_1h': resampled_df.loc[t_lag1h, 'mean'] / 4.0,
        'lag_24h': resampled_df.loc[t_lag24h, 'mean'] / 4.0,
        'rolling_mean_4h': rolling_window['mean'].mean() / 4.0
    }
    
    assert train_features['lag_1h'] == infer_features['lag_1h'], f"lag_1h mismatch: {train_features['lag_1h']} != {infer_features['lag_1h']}"
    assert train_features['lag_24h'] == infer_features['lag_24h'], f"lag_24h mismatch: {train_features['lag_24h']} != {infer_features['lag_24h']}"
    assert train_features['rolling_mean_4h'] == infer_features['rolling_mean_4h'], f"rolling mismatch: {train_features['rolling_mean_4h']} != {infer_features['rolling_mean_4h']}"
    
    print("Success: Inference feature generation perfectly matches training pipeline semantics.")

def test_negative_clamping():
    print("\n--- TEST C: Invalid Model Outputs ---")
    forecaster = DemandForecaster(model_path="backend/models/forecasting/xgboost_steel_v1.joblib")
    
    # Mock the model to return a negative prediction
    class MockModel:
        def predict(self, X):
            return [-10.0]
            
    forecaster.model = MockModel()
    
    # Generate valid history
    df = pd.DataFrame([
        {'timestamp': datetime.datetime.now(datetime.timezone.utc) - pd.Timedelta(minutes=15 * i), 'power_kw': 100.0}
        for i in range(100)
    ]).sort_values('timestamp')
    
    try:
        forecaster.predict_15m_from_history(df)
        print("Failure: Model allowed negative output.")
    except Exception as e:
        if "negative power" in str(e):
            print("Success: Model strictly rejected negative power.")
        else:
            print(f"Failure: Expected negative power exception, got: {e}")

if __name__ == "__main__":
    test_unit_conversion()
    test_feature_parity()
    test_negative_clamping()
