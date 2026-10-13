import requests
import datetime
import time

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
        "frequency_hz": 50.0,
        "power_factor": 0.96,
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
    # Start 97 * 15m ago
    start_time = now - datetime.timedelta(minutes=15 * 97)
    
    for i in range(98):
        ts = start_time + datetime.timedelta(minutes=15 * i)
        payload = {
            "timestamp": ts.isoformat(),
            "source": "SIMULATED_RASPI",
            "device_id": "RPi-METER-01",
        "voltage": 230.4,
        "current": 1.82,
        "frequency_hz": 50.0,
        "power_factor": 0.96,
            "voltage": 230.4,
            "current": 1.82,
            "active_power_kw": 10.0 + (i * 0.1),
            "energy_kwh": 100.0,
            "frequency_hz": 50.0,
            "power_factor": 0.96,
            "quality": "GOOD",
            "machine_state": "RUNNING"
        }
        requests.post(f"{API_URL}/api/telemetry/ingest", json=payload)
        
    res = requests.get(f"{API_URL}/api/factory/state?mode=LIVE").json()
    forecasts = res.get("forecast", [])
    print("Forecast Count:", len(forecasts))
    if len(forecasts) > 0:
        print("Prediction:", forecasts[0])

def test_missing_interval():
    print("\n--- TEST C: Missing Interval (Drop lag_1h) ---")
    # We will send a fresh stream of 98 items, but skip the one at `now - 1h` (which is lag_1h for prediction at now + 15m)
    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now - datetime.timedelta(minutes=15 * 97)
    
    # We want to skip the reading at t_lag1h = (now + 15m) - 1h = now - 45m.
    # now - 45m is 3 intervals ago from `now`. So it's i=94.
    for i in range(98):
        if i == 94:
            continue # skip lag_1h
        ts = start_time + datetime.timedelta(minutes=15 * i)
        payload = {
            "timestamp": ts.isoformat(),
            "source": "SIMULATED_RASPI",
            "device_id": "RPi-METER-01",
        "voltage": 230.4,
        "current": 1.82,
        "frequency_hz": 50.0,
        "power_factor": 0.96,
            "active_power_kw": 10.0 + (i * 0.1),
            "energy_kwh": 100.0,
            "machine_state": "RUNNING"
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
        "voltage": 230.4,
        "current": 1.82,
        "frequency_hz": 50.0,
        "power_factor": 0.96,
        "active_power_kw": 50.0,
        "energy_kwh": 100.0,
        "machine_state": "RUNNING"
    }
    r = requests.post(f"{API_URL}/api/telemetry/ingest", json=payload)
    print("Future Ingest Status:", r.status_code)
    
    status = requests.get(f"{API_URL}/api/telemetry/source-status").json()
    print("Source Status after future reading:", status.get("source_status"))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "short":
            test_short_stream()
        elif sys.argv[1] == "long":
            test_long_stream()
        elif sys.argv[1] == "missing":
            test_missing_interval()
        elif sys.argv[1] == "future":
            test_future_dated()
