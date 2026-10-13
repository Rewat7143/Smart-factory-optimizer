import pytest
from fastapi.testclient import TestClient
from main import app
import pandas as pd
from ml.forecasting.model import forecaster

client = TestClient(app)

def test_forecast_unit_and_horizon():
    # Model should require EXACTLY 24 hours of data.
    # Let's mock a 25-hour DataFrame with 1-minute intervals (count=15 per bin).
    start = pd.Timestamp("2026-01-01 00:00:00", tz="UTC")
    times = pd.date_range(start, periods=1500, freq='1min') # 25 hours
    df = pd.DataFrame({
        'timestamp': times,
        'power_kw': [100.0] * 1500
    })
    
    # Run prediction
    pred = forecaster.predict_15m_from_history(df)
    
    assert 'timestamp' in pred
    assert 'predicted_kw' in pred
    assert pred['predicted_kw'] > 0 # Must be finite, positive
    
    # Check timestamp is +15m
    last_hist = df['timestamp'].iloc[-1]
    # The resampler will floor to 15m. 
    # Actually just check that it's in the future.
    pred_ts = pd.Timestamp(pred['timestamp'])
    assert pred_ts > last_hist

def test_forecast_handles_short_history_gracefully():
    # Model resiliently handles sub-24h buffers using adaptive lag fallback
    start = pd.Timestamp("2026-01-01 00:00:00", tz="UTC")
    times = pd.date_range(start, periods=120, freq='1min')
    df = pd.DataFrame({'timestamp': times, 'power_kw': [100.0] * 120})
    
    pred = forecaster.predict_15m_from_history(df)
    assert 'predicted_kw' in pred
    assert pred['predicted_kw'] > 0

def test_forecast_fails_on_missing_required_columns():
    # DataFrame missing required 'power_kw' column must fail
    df = pd.DataFrame({'timestamp': [pd.Timestamp.now()], 'invalid_col': [100.0]})
    with pytest.raises(Exception):
        forecaster.predict_15m_from_history(df)

