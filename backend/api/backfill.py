import datetime
import pandas as pd
import uuid
import os
from schemas.energy import DataSource, DataQuality, EnergyReading
from simulator.machines import MachineState
from api.telemetry import TelemetryPayload
from api import telemetry

def ensure_commissioning_data():
    if len(telemetry.recent_readings_cache) > 24 * 60:
        return
        
    print("Backfilling commissioning telemetry data (24.5 hours) into memory cache...")
    df = pd.DataFrame()
    uci_path = 'data/industrial/uci_steel/raw_data.csv'
    if os.path.exists(uci_path):
        try:
            df = pd.read_csv(uci_path)
            df = df.tail(100).copy()
        except Exception as e:
            print(f"Could not read UCI data for backfill: {e}")
            
    now = datetime.datetime.now(datetime.timezone.utc)
    num_readings = int(24.5 * 60)
    start_time = now - datetime.timedelta(minutes=num_readings)
    
    new_readings = []
    
    for i in range(num_readings):
        ts = start_time + datetime.timedelta(minutes=i)
        
        hour = ts.hour
        if 8 <= hour <= 18:
            power_kw = 80.0 + (i % 10)
        else:
            power_kw = 35.0 + (i % 5)
            
        payload = TelemetryPayload(
            timestamp=ts.isoformat(),
            source="SIMULATED_RASPI",
            device_id="RPi-METER-01",
            voltage=230.5,
            current=power_kw / 0.230 / 3,
            active_power_kw=power_kw,
            energy_kwh=power_kw * 0.25,
            frequency_hz=50.0,
            power_factor=0.98,
            quality="GOOD",
            machine_state="RUNNING"
        )
        
        reading = EnergyReading(
            timestamp=ts,
            factory_id='fac_001',
            asset_id="RPi-METER-01",
            voltage_v=payload.voltage,
            current_a=payload.current,
            active_power_kw=payload.active_power_kw,
            energy_kwh=payload.energy_kwh,
            frequency_hz=payload.frequency_hz,
            power_factor=payload.power_factor,
            machine_state=MachineState(payload.machine_state),
            data_source=DataSource(payload.source),
            data_quality=DataQuality(payload.quality)
        )
        new_readings.append(reading)
        
    telemetry.recent_readings_cache.extend(new_readings)
    telemetry.latest_reading = new_readings[-1]
    
    if len(telemetry.recent_readings_cache) > telemetry.MAX_CACHE_SIZE:
        telemetry.recent_readings_cache = telemetry.recent_readings_cache[-telemetry.MAX_CACHE_SIZE:]
        
    print(f"Successfully backfilled {len(new_readings)} commissioning readings. Cache size: {len(telemetry.recent_readings_cache)}")
