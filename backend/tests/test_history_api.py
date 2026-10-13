import pytest
from fastapi.testclient import TestClient
from main import app
import datetime

client = TestClient(app)

def test_custom_forecast_api():
    # Construct history of 1440 points (24 hours at 1min freq)
    base_time = datetime.datetime(2026, 1, 2, 0, 0, 0, tzinfo=datetime.timezone.utc)
    history = []
    for i in range(1500):
        ts = (base_time + datetime.timedelta(minutes=i)).isoformat()
        history.append({
            "timestamp": ts,
            "active_power_kw": 100.0
        })
        
    res = client.post("/api/forecast/custom", json={"history": history})
    assert res.status_code == 200
    data = res.json()
    assert "forecast" in data
    assert data["forecast"] is not None
    assert "predicted_kw" in data["forecast"]
