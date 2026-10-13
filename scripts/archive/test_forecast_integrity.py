import requests
import datetime
import time

API_URL = "http://127.0.0.1:8000"

def test_short_stream():
    print("\n--- TEST 1: Short Stream (Insufficient History) ---")
    # Send 5 readings, 1 second apart
    for i in range(5):
        payload = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
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
        time.sleep(0.1)
        
    res = requests.get(f"{API_URL}/api/factory/state?mode=LIVE").json()
    print("Live Status:", res.get("live_status"))
    print("Source:", res.get("data_source"))
    print("Forecast Count:", len(res.get("forecast", [])))
    if len(res.get("forecast", [])) == 0:
        print("Success: Forecast unavailable due to insufficient history.")

def test_long_stream():
    print("\n--- TEST 2: Long Stream (24h History) ---")
    # We will simulate injecting 24.5 hours of historical telemetry directly.
    # Because sending 100 requests is fast, we will send 100 requests spaced by 15 minutes in their timestamps.
    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now - datetime.timedelta(hours=24, minutes=30)
    
    for i in range(100):
        ts = start_time + datetime.timedelta(minutes=15 * i)
        payload = {
            "timestamp": ts.isoformat(),
            "source": "SIMULATED_RASPI",
            "device_id": "RPi-METER-01",
            "voltage": 230.4,
            "current": 1.82,
            "active_power_kw": 0.400 + (i * 0.001),
            "energy_kwh": 12.0 + (i * 0.1),
            "frequency_hz": 50.0,
            "power_factor": 0.96,
            "quality": "GOOD"
        }
        requests.post(f"{API_URL}/api/telemetry/ingest", json=payload)
        
    res = requests.get(f"{API_URL}/api/factory/state?mode=LIVE").json()
    print("Live Status:", res.get("live_status"))
    print("Forecast Count:", len(res.get("forecast", [])))
    if len(res.get("forecast", [])) > 0:
        print("Success: Genuine numerical prediction returned.")
        print("Prediction:", res.get("forecast")[0])
    else:
        print("Failure: Forecast still unavailable.")
        
if __name__ == "__main__":
    test_short_stream()
    test_long_stream()
