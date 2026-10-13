import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import datetime
import math
import uuid
from database.db import insert_telemetry, delete_test_run
from api.google_sheets import gsheets_db

# Deterministic test parameters
RUN_ID = "test_run_72h"

def generate_three_day_data(dry_run=True):
    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now - datetime.timedelta(days=3)
    
    # 1 minute intervals for 72 hours = 4320 records
    intervals = 72 * 60
    
    print(f"Generating 72-hour historical test dataset from {start_time} to {now}")
    print(f"Interval: 1 minute ({intervals} records)")
    
    records = []
    cumulative_energy = 0.0
    
    for i in range(intervals):
        ts = start_time + datetime.timedelta(minutes=i)
        
        # Plausible industrial profile
        # Base load ~ 20kW
        # Shifts: 8AM-4PM high load (80-120kW), 4PM-12AM medium (40-60kW), 12AM-8AM low (20-30kW)
        hour = ts.hour
        
        if 8 <= hour < 16:
            base_kw = 90.0 + 10 * math.sin(i / 60.0) # Slow fluctuation
            # Add a peak event on day 2 at 2PM
            if ts.day == (now - datetime.timedelta(days=1)).day and hour == 14:
                base_kw += 50.0 * math.exp(-((ts.minute - 30)**2) / 50.0)
        elif 16 <= hour < 24:
            base_kw = 50.0 + 5 * math.cos(i / 30.0)
        else:
            base_kw = 25.0 + 2 * math.sin(i / 15.0)
            
        power_kw = base_kw
        
        # Energy calculation
        # power (kW) * time (hours) = energy (kWh)
        energy_increment = power_kw * (1.0 / 60.0)
        cumulative_energy += energy_increment
        
        voltage = 230.0 + 2.0 * math.sin(i / 120.0)
        current = (power_kw * 1000) / (voltage * 1.732 * 0.9) if power_kw > 0 else 0
        
        record = {
            "record_id": f"{RUN_ID}_{i}",
            "timestamp": ts.isoformat(),
            "factory_id": f"fac_001_{RUN_ID}",
            "asset_id": "MAIN_METER",
            "voltage_v": round(voltage, 2),
            "current_a": round(current, 2),
            "active_power_kw": round(power_kw, 2),
            "energy_kwh": round(cumulative_energy, 2),
            "frequency_hz": round(50.0 + 0.1 * math.sin(i / 10.0), 3),
            "power_factor": 0.92,
            "machine_state": "RUNNING",
            "data_source": "HISTORICAL_TEST",
            "data_quality": "SIMULATED"
        }
        records.append(record)
        
    if dry_run:
        print(f"[DRY RUN] Would insert {len(records)} records.")
        print("Sample of first record:")
        print(records[0])
        print("Sample of peak record (Day 2, 2PM roughly):")
        peak_candidates = [r for r in records if 'T14:30' in r['timestamp']]
        if peak_candidates:
            print(peak_candidates[0])
        return

    print("Inserting into local database...")
    success_count = 0
    for r in records:
        if insert_telemetry(r):
            success_count += 1
            
    print(f"Successfully inserted {success_count} / {len(records)} records into DB.")
    
    print("Flushing to Google Sheets buffer...")
    gsheets_db.connect()
    gsheets_db.append_telemetry(records)
    gsheets_db.flush_telemetry()
    print("Sheets append complete. (Note: Writes may be batched/delayed in background).")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Actually run the insertion")
    parser.add_argument("--cleanup", action="store_true", help="Delete the generated test records")
    args = parser.parse_args()
    
    if args.cleanup:
        delete_test_run(RUN_ID)
        print(f"Cleaned up records matching RUN_ID: {RUN_ID}")
    else:
        generate_three_day_data(dry_run=not args.execute)
