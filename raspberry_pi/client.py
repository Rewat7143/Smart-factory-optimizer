import os
import time
import requests
import random
from datetime import datetime, timezone

API_BASE_URL = os.getenv("ENERGY_API_BASE_URL", "http://localhost:8000")
DEVICE_ID = os.getenv("DEVICE_ID", "RPi-METER-01")
INTERVAL = int(os.getenv("TELEMETRY_INTERVAL_SECONDS", "1"))

def read_meter_values(accumulated_wh: float, accumulated_vah: float, load_seconds: float):
    """
    Simulates reading all 27 Modbus registers from the L&T WL 4400 Multi-Function Meter:
    Addresses:
      40101: Watts Total (float)
      40103: Watts R phase (float)
      40105: Watts Y phase (float)
      40107: Watts B phase (float)
      40117: PF Avg (inst) (float)
      40119: PF R phase (float)
      40121: PF Y phase (float)
      40123: PF B phase (float)
      40125: VA total (float)
      40127: VA R phase (float)
      40129: VA Y phase (float)
      40131: VA B phase (float)
      40133: VL L average (float)
      40135: VR Y phase (float)
      40137: VY B phase (float)
      40139: VB R phase (float)
      40141: VL N average (float)
      40143: V R phase (float)
      40145: V Y phase (float)
      40147: V B phase (float)
      40149: Current Total (float)
      40151: Current R phase (float)
      40153: Current Y phase (float)
      40155: Current B phase (float)
      40157: Frequency (float)
      40159: Wh (float)
      40161: VAh (float)
      40217: Load Hours (Unsigned long)
    """
    # 1. Line-to-Neutral Phase Voltages (V) around 230V
    v_r = round(230.2 + random.uniform(-1.2, 1.2), 2)
    v_y = round(231.1 + random.uniform(-1.2, 1.2), 2)
    v_b = round(229.8 + random.uniform(-1.2, 1.2), 2)
    v_ln_avg = round((v_r + v_y + v_b) / 3.0, 2)

    # 2. Line-to-Line Voltages (V) approx sqrt(3) * V_ln (~398V - 400V)
    sqrt3 = 1.73205
    v_ry = round(v_ln_avg * sqrt3 + random.uniform(-0.8, 0.8), 2)
    v_yb = round(v_ln_avg * sqrt3 + random.uniform(-0.8, 0.8), 2)
    v_br = round(v_ln_avg * sqrt3 + random.uniform(-0.8, 0.8), 2)
    v_ll_avg = round((v_ry + v_yb + v_br) / 3.0, 2)

    # 3. Power Factor per phase (~0.97 healthy grid standard)
    pf_r = round(0.968 + random.uniform(-0.006, 0.006), 3)
    pf_y = round(0.972 + random.uniform(-0.006, 0.006), 3)
    pf_b = round(0.965 + random.uniform(-0.006, 0.006), 3)
    pf_avg = round((pf_r + pf_y + pf_b) / 3.0, 3)

    # 4. Active Power per phase (Watts)
    # Steady factory baseline runs at ~91.1 kW (safe, compliant below 93 kW limit)
    # Surges are controlled via operator demand trigger or API
    watts_r = round(30310.0 + random.uniform(-80.0, 80.0), 1)
    watts_y = round(30250.0 + random.uniform(-80.0, 80.0), 1)
    watts_b = round(30360.0 + random.uniform(-80.0, 80.0), 1)
    watts_total = round(watts_r + watts_y + watts_b, 1)

    # 5. Apparent Power per phase (VA = Watts / PF) - Totaling ~94.0 kVA - 96.8 kVA
    va_r = round(watts_r / pf_r, 1)
    va_y = round(watts_y / pf_y, 1)
    va_b = round(watts_b / pf_b, 1)
    va_total = round(va_r + va_y + va_b, 1)

    # 6. Current per phase (Amps = VA / V_ln)
    current_r = round(va_r / v_r, 2)
    current_y = round(va_y / v_y, 2)
    current_b = round(va_b / v_b, 2)
    current_total = round(current_r + current_y + current_b, 2)

    # 7. Frequency (Hz)
    frequency = round(50.01 + random.uniform(-0.04, 0.04), 2)

    # 8. Energy Accumulation (Wh & VAh) and Load Hours
    interval_hours = INTERVAL / 3600.0
    accumulated_wh += (watts_total * interval_hours)
    accumulated_vah += (va_total * interval_hours)
    load_seconds += INTERVAL
    load_hours = int(load_seconds // 3600)

    meter_data = {
        # Active Power
        "watts_total": watts_total,
        "watts_r": watts_r,
        "watts_y": watts_y,
        "watts_b": watts_b,

        # Power Factor
        "pf_avg": pf_avg,
        "pf_r": pf_r,
        "pf_y": pf_y,
        "pf_b": pf_b,

        # Apparent Power
        "va_total": va_total,
        "va_r": va_r,
        "va_y": va_y,
        "va_b": va_b,

        # Line-to-Line Voltage
        "v_ll_avg": v_ll_avg,
        "v_ry": v_ry,
        "v_yb": v_yb,
        "v_br": v_br,

        # Line-to-Neutral Voltage
        "v_ln_avg": v_ln_avg,
        "v_r": v_r,
        "v_y": v_y,
        "v_b": v_b,

        # Current
        "current_total": current_total,
        "current_r": current_r,
        "current_y": current_y,
        "current_b": current_b,

        # Frequency
        "frequency": frequency,

        # Energy & Runtime
        "energy_wh": round(accumulated_wh, 2),
        "energy_vah": round(accumulated_vah, 2),
        "load_hours": load_hours,

        # Compatibility fields
        "voltage": v_ln_avg,
        "current": current_total,
        "active_power_kw": round(watts_total / 1000.0, 3),
        "energy_kwh": round(accumulated_wh / 1000.0, 3),
        "frequency_hz": frequency,
        "power_factor": pf_avg,
        "quality": "GOOD",
        "machine_state": "RUNNING"
    }

    return meter_data, accumulated_wh, accumulated_vah, load_seconds

def main():
    print("=" * 75)
    print("🚀 Starting Raspberry Pi Energy Simulator Client")
    print(f"📡 Target API : {API_BASE_URL}/api/telemetry/ingest")
    print(f"📟 Device ID  : {DEVICE_ID}")
    print(f"⏱️  Interval   : {INTERVAL}s")
    print(f"📊 Protocol   : Modbus RTU Memory Map Emulation (Addresses 40101 - 40217)")
    print("=" * 75)
    
    # Check API health
    try:
        res = requests.get(f"{API_BASE_URL}/api/system/status", timeout=5)
        print(f"🟢 API Health check: {res.json()}")
    except Exception as e:
        print(f"🟡 Warning: API not reachable at startup ({e}). Retrying in loop...")
        
    accumulated_wh = 175131297.0   # 175,131.297 kWh baseline
    accumulated_vah = 193873100.0  # 193,873.1 kVAh baseline
    load_seconds = 1420 * 3600 # Start at 1420 hours
    
    while True:
        try:
            # 1. Read / simulate all 27 meter parameters
            raw_data, accumulated_wh, accumulated_vah, load_seconds = read_meter_values(
                accumulated_wh, accumulated_vah, load_seconds
            )
            
            # 2. Format Ingestion Payload
            payload = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "SIMULATED_RASPI",
                "device_id": DEVICE_ID,
                **raw_data
            }
            
            # 3. Send to FastAPI
            response = requests.post(
                f"{API_BASE_URL}/api/telemetry/ingest",
                json=payload,
                timeout=3
            )
            
            now_str = datetime.now().strftime('%H:%M:%S')
            if response.status_code == 200:
                print(f"[{now_str}] SUCCESS | 27 Parameters Ingested")
                print(f"  ├── Active Power (40101-40107) : {payload['watts_total']:.1f} W ({payload['active_power_kw']:.3f} kW) | R:{payload['watts_r']:.1f}W, Y:{payload['watts_y']:.1f}W, B:{payload['watts_b']:.1f}W")
                print(f"  ├── Apparent Pwr (40125-40131) : {payload['va_total']:.1f} VA | R:{payload['va_r']:.1f}VA, Y:{payload['va_y']:.1f}VA, B:{payload['va_b']:.1f}VA")
                print(f"  ├── Power Factor (40117-40123) : Avg={payload['pf_avg']:.3f} | R={payload['pf_r']:.3f}, Y={payload['pf_y']:.3f}, B={payload['pf_b']:.3f}")
                print(f"  ├── Voltage V_LN (40141-40147) : Avg={payload['v_ln_avg']:.1f}V | VR:{payload['v_r']:.1f}V, VY:{payload['v_y']:.1f}V, VB:{payload['v_b']:.1f}V")
                print(f"  ├── Voltage V_LL (40133-40139) : Avg={payload['v_ll_avg']:.1f}V | VRY:{payload['v_ry']:.1f}V, VYB:{payload['v_yb']:.1f}V, VBR:{payload['v_br']:.1f}V")
                print(f"  ├── Current      (40149-40155) : Tot={payload['current_total']:.2f}A | IR:{payload['current_r']:.2f}A, IY:{payload['current_y']:.2f}A, IB:{payload['current_b']:.2f}A")
                print(f"  ├── Frequency    (40157)       : {payload['frequency']:.2f} Hz")
                print(f"  ├── Energy       (40159-40161) : Wh={payload['energy_wh']:.1f} Wh | VAh={payload['energy_vah']:.1f} VAh")
                print(f"  └── Load Hours   (40217)       : {payload['load_hours']} hrs")
                print("-" * 75)
            else:
                print(f"[{now_str}] ERROR | HTTP {response.status_code} | {response.text}")
                
        except requests.exceptions.RequestException as e:
            now_str = datetime.now().strftime('%H:%M:%S')
            print(f"[{now_str}] CONNECTION ERROR | Retrying... ({e})")
            
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
