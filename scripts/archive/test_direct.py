import sys
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

payload = {
    "timestamp": "2026-10-05T18:40:00+00:00",
    "source": "RASPBERRY_PI",
    "device_id": "RPi-METER-01",
    "voltage": 230.5,
    "current": 12.4,
    "active_power_kw": 2.85,
    "energy_kwh": 145.0,
    "frequency_hz": 50.01,
    "power_factor": 0.98,
    "quality": "GOOD",
    "machine_state": "RUNNING"
}
try:
    res = client.post("/api/telemetry/ingest", json=payload)
    print("STATUS:", res.status_code)
    print("RESPONSE:", json.dumps(res.json(), indent=2))
except Exception as e:
    print("FAILED:", e)

res2 = client.get("/api/telemetry/latest")
print("LATEST:", json.dumps(res2.json(), indent=2))
