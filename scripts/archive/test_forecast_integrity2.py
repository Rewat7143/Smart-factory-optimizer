import requests
import datetime
import time
import random

API_URL = "http://127.0.0.1:8000"

def test_short_stream():
    print("\n--- TEST A: Short Stream (Insufficient History) ---")
    now = datetime.datetime.now(datetime.timezone.utc)
    for i in range(5):
        ts = now - datetime.timedelta(seconds=(5-i))
        payload = {
            "timestamp": ts.isoformat(),
            "source": "SIMULATED_RASPI",
            "device_id": "RPi-METER-01",
            "voltage": 230.4,
            "current": 1.82,
            "active_power_kw": 0.412 + (i * 0.01),
            "energy_kwh": 12.43,
            "frequency_hz": 50.01,
            "power_factor": 0.96,
            "quality": "GOOD"
        }
        requests.post(f"{API_URL}/api/telemetry/ingest", json=payload)
        
    res = requests.get(f"{API_URL}/api/factory/state?mode=LIVE").json()
    print("Forecast Count:", len(res.get("forecast", [])))

def test_long_stream():
    print("\n--- TEST B: Long Stream (24h History, Chronological) ---")
    now = datetime.datetime.now(datetime.timezone.utc)
    # To end exactly at `now`, we start 97 * 15m ago. (97 intervals = 24.25 hours)
    start_time = now - datetime.timedelta(minutes=15 * 97)
    
    # Generate 98 readings (indices 0 to 97), so the last one is exactly `now`.
    for i in range(98):
        ts = start_time + datetime.timedelta(minutes=15 * i)
        payload = {
            "timestamp": ts.isoformat(),
            "source": "SIMULATED_RASPI",
            "device_id": "RPi-METER-01",
            "voltage": 230.4,
            "current": 1.82,
            "active_power_kw": 10.0 + (i * 0.1),
            "energy_kwh": 100.0,
            "frequency_hz": 50.0,
            "power_factor": 0.96,
            "quality": "GOOD"
        }
        requests.post(f"{API_URL}/api/telemetry/ingest", json=payload)
        
    res = requests.get(f"{API_URL}/api/factory/state?mode=LIVE").json()
    forecasts = res.get("forecast", [])
    print("Forecast Count:", len(forecasts))
    if len(forecasts) > 0:
        print("Prediction:", forecasts[0])

def test_missing_interval():
    print("\n--- TEST C: Missing Interval ---")
    # Clear cache by restarting backend (we will just wait for actual backend restart in run script, or we can just inject a completely new stream that skips the exact lag_1h requirement)
    # Actually, we can just send a stream that stops 2 hours ago.
    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now - datetime.timedelta(minutes=15 * 100)
    
    for i in range(90): # Stops 10 * 15m = 2.5 hours ago
        ts = start_time + datetime.timedelta(minutes=15 * i)
        payload = {
            "timestamp": ts.isoformat(),
            "source": "SIMULATED_RASPI",
            "device_id": "RPi-METER-01",
            "voltage": 230.4,
            "current": 1.82,
            "active_power_kw": 10.0,
            "energy_kwh": 100.0,
            "frequency_hz": 50.0,
            "power_factor": 0.96,
            "quality": "GOOD"
        }
        requests.post(f"{API_URL}/api/telemetry/ingest", json=payload)
        
    res = requests.get(f"{API_URL}/api/factory/state?mode=LIVE").json()
    print("Forecast Count (after gap):", len(res.get("forecast", [])))

def test_future_dated():
    print("\n--- TEST D: Future-dated and Stale Readings ---")
    now = datetime.datetime.now(datetime.timezone.utc)
    
    # Future reading
    future_ts = now + datetime.timedelta(hours=1)
    payload = {
        "timestamp": future_ts.isoformat(),
        "source": "SIMULATED_RASPI",
        "device_id": "RPi-METER-01",
        "active_power_kw": 50.0,
        "energy_kwh": 100.0,
        "machine_state": "RUNNING",
        "quality": "GOOD"
    }
    r = requests.post(f"{API_URL}/api/telemetry/ingest", json=payload)
    print("Future Ingest Status:", r.status_code)
    
    status = requests.get(f"{API_URL}/api/telemetry/source-status").json()
    print("Source Status after future reading:", status.get("source_status"))

if __name__ == "__main__":
    test_short_stream()
    test_long_stream()
    test_missing_interval()
    test_future_dated()
