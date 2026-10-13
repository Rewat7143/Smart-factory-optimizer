import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timezone, timedelta
import time

client = TestClient(app)

def test_live_pipeline_isolation():
    # 1. Initially, LIVE should be OFFLINE
    res = client.get("/api/factory/state?mode=LIVE")
    assert res.status_code == 200
    assert res.json()["live_status"] == "OFFLINE", "Should be offline initially"
    
    # 2. Ingest fresh valid payload
    now = datetime.now(timezone.utc)
    payload = {
        "timestamp": now.isoformat(),
        "source": "RASPBERRY_PI",
        "device_id": "L&T_WL4400_01",
        "voltage": 415.0,
        "current": 100.0,
        "active_power_kw": 85.5,
        "energy_kwh": 1000.5,
        "frequency_hz": 50.0,
        "power_factor": 0.95,
        "quality": "GOOD",
        "machine_state": "RUNNING"
    }
    post_res = client.post("/api/telemetry/ingest", json=payload)
    assert post_res.status_code == 200
    
    # 3. LIVE should now be ONLINE
    res2 = client.get("/api/factory/state?mode=LIVE")
    assert res2.status_code == 200
    assert res2.json()["live_status"] == "CONNECTED", "Should be CONNECTED after fresh ingestion"
    assert res2.json()["current_demand_kw"] == 85.5, "Live demand should match payload exactly"
    
    # 4. Simulation must remain unaffected
    res_sim = client.get("/api/factory/state?mode=SIMULATION")
    assert res_sim.json()["data_source"] == "SIMULATOR", "Simulation should remain completely isolated"
    assert res_sim.json()["current_demand_kw"] != 85.5, "Simulation demand must NOT be the physical reading"
    
    # 5. Stale test
    # Ingest a stale payload (e.g. 5 minutes old)
    stale_time = now - timedelta(minutes=5)
    stale_payload = payload.copy()
    stale_payload["timestamp"] = stale_time.isoformat()
    client.post("/api/telemetry/ingest", json=stale_payload)
    
    res_stale = client.get("/api/factory/state?mode=LIVE")
    assert res_stale.json()["live_status"] == "OFFLINE", "Stale telemetry must result in OFFLINE status"
    
