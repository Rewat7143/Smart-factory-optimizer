import datetime
import os
import sys

sys.path.append(os.path.abspath('backend'))
from main import app
from fastapi.testclient import TestClient
from api import telemetry

client = TestClient(app)

def test_telemetry_payload_validation():
    print("\n--- TEST: Telemetry Payload Contract ---")
    valid_payload = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": "RASPBERRY_PI",
        "device_id": "RPi-METER-01",
        "voltage": 230.5,
        "current": 10.2,
        "active_power_kw": 2.35,
        "energy_kwh": 100.5,
        "frequency_hz": 50.0,
        "power_factor": 0.98,
        "quality": "GOOD",
        "machine_state": "RUNNING"
    }
    
    response = client.post("/api/telemetry/ingest", json=valid_payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("Success: Valid Modbus payload accepted.")
    
    invalid_payload = valid_payload.copy()
    del invalid_payload["active_power_kw"]
    
    response = client.post("/api/telemetry/ingest", json=invalid_payload)
    assert response.status_code == 422
    print("Success: Invalid payload cleanly rejected.")

def test_live_versus_simulation_isolation():
    print("\n--- TEST: Live vs Simulation Mode Isolation ---")
    telemetry.latest_reading = None # Force offline
    
    res_sim = client.get("/api/factory/state?mode=SIMULATION")
    assert res_sim.status_code == 200
    assert res_sim.json().get("live_status") != "OFFLINE"
    
    res_live = client.get("/api/factory/state?mode=LIVE")
    assert res_live.status_code == 200
    assert res_live.json().get("live_status") == "OFFLINE"
    print("Success: Mode isolation enforced (LIVE safely returns OFFLINE when disconnected).")

if __name__ == "__main__":
    test_telemetry_payload_validation()
    test_live_versus_simulation_isolation()
