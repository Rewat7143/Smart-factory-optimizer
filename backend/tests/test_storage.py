import pytest
from database.db import insert_telemetry, query_telemetry, count_telemetry, delete_test_run, get_connection
import datetime
import uuid

def test_telemetry_insert_and_duplicate():
    rec_id = str(uuid.uuid4())
    record = {
        "record_id": rec_id,
        "timestamp": "2026-01-01T00:00:00Z",
        "factory_id": "fac_test_db",
        "asset_id": "METER_1",
        "active_power_kw": 100.0,
        "energy_kwh": 10.0,
        "data_source": "HISTORICAL_TEST",
        "data_quality": "SIMULATED"
    }
    
    # Insert 1
    success1 = insert_telemetry(record)
    assert success1 is True
    
    # Insert duplicate
    success2 = insert_telemetry(record)
    assert success2 is True # UPSERT / DO NOTHING behaves as successful operation in terms of avoiding crashes
    
    # Verify exactly 1 record with this ID
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM telemetry WHERE record_id = ?", (rec_id,)).fetchone()[0]
        assert count == 1
        
    delete_test_run("fac_test_db")

def test_query_and_count():
    base_time = datetime.datetime(2026, 1, 2, 0, 0, 0, tzinfo=datetime.timezone.utc)
    for i in range(10):
        rec_id = f"test_q_{i}"
        ts = (base_time + datetime.timedelta(minutes=i)).isoformat()
        insert_telemetry({
            "record_id": rec_id,
            "timestamp": ts,
            "factory_id": "fac_test_query",
            "asset_id": "METER_Q",
            "active_power_kw": 10.0,
            "data_source": "HISTORICAL_TEST",
            "energy_kwh": 1.0
        })
        
    count = count_telemetry("2026-01-02T00:00:00+00:00", "2026-01-02T00:15:00+00:00", source="HISTORICAL_TEST")
    assert count == 10
    
    records = query_telemetry("2026-01-02T00:00:00+00:00", "2026-01-02T00:05:00+00:00", source="HISTORICAL_TEST")
    assert len(records) == 6 # 0, 1, 2, 3, 4, 5
    
    delete_test_run("fac_test_query")
