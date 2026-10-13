import re

with open('backend/api/telemetry.py', 'r') as f:
    content = f.read()

# Add database import
if 'from database.db import insert_telemetry' not in content:
    content = content.replace('from api.google_sheets import gsheets_db', 
                              'from api.google_sheets import gsheets_db\nfrom database.db import insert_telemetry')

# Update ingest_telemetry
old_block = """    # Send to Google Sheets storage module
    gs_record = reading.dict()
    gs_record['record_id'] = str(uuid.uuid4())
    gs_record['timestamp'] = ts.isoformat()
    gs_record['machine_state'] = payload.machine_state
    gs_record['source'] = payload.source
    gs_record['quality'] = payload.quality
    gsheets_db.append_telemetry([gs_record])
    
    live_device_state[payload.device_id] = {
        "last_seen": datetime.now(timezone.utc),
        "source": payload.source,
        "packet_count": live_device_state.get(payload.device_id, {}).get("packet_count", 0) + 1
    }
    
    return {
        "accepted": True,
        "device_id": payload.device_id,
        "source": payload.source,
        "timestamp": payload.timestamp,
        "server_timestamp": datetime.now(timezone.utc).isoformat()
    }"""

new_block = """    record_id = str(uuid.uuid4())
    
    # 1. Authoritative Database Persistence
    db_record = {
        "record_id": record_id,
        "timestamp": ts.isoformat(),
        "factory_id": "fac_001",
        "asset_id": payload.device_id,
        "voltage_v": payload.voltage,
        "current_a": payload.current,
        "active_power_kw": payload.active_power_kw,
        "energy_kwh": payload.energy_kwh,
        "frequency_hz": payload.frequency_hz,
        "power_factor": payload.power_factor,
        "machine_state": payload.machine_state,
        "data_source": payload.source,
        "data_quality": payload.quality
    }
    db_success = insert_telemetry(db_record)
    
    # 2. Google Sheets Buffer
    gs_record = reading.dict()
    gs_record['record_id'] = record_id
    gs_record['timestamp'] = ts.isoformat()
    gs_record['machine_state'] = payload.machine_state
    gs_record['source'] = payload.source
    gs_record['quality'] = payload.quality
    gsheets_db.append_telemetry([gs_record])
    
    live_device_state[payload.device_id] = {
        "last_seen": datetime.now(timezone.utc),
        "source": payload.source,
        "packet_count": live_device_state.get(payload.device_id, {}).get("packet_count", 0) + 1
    }
    
    return {
        "accepted": True,
        "device_id": payload.device_id,
        "source": payload.source,
        "timestamp": payload.timestamp,
        "server_timestamp": datetime.now(timezone.utc).isoformat(),
        "persistence": {
            "database": "PERSISTED" if db_success else "FAILED",
            "google_sheets": "PENDING_SYNC"
        }
    }"""

content = content.replace(old_block, new_block)

with open('backend/api/telemetry.py', 'w') as f:
    f.write(content)
