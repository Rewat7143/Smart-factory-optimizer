import requests
import time

def print_state():
    opt = requests.post('http://localhost:8000/api/optimize').json()
    demo = requests.get('http://localhost:8000/api/demo/state').json()
    print(f"[{demo['step']}/14] {demo['message']}")
    print(f"Demand: {opt['pipeline']['current_demand']} kW | Forecast: {opt['pipeline']['predicted_peak']} kW | Risk: {opt['pipeline']['peak_risk']}")
    print(f"Optimizer: {opt['optimization']['status']}")
    print("-" * 50)

print("Starting Demo...")
requests.post('http://localhost:8000/api/demo/start')

for _ in range(12):
    print_state()
    time.sleep(4.0)

