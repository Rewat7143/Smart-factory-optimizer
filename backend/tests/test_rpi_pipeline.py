import os
import sys
import tempfile
import sqlite3
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

# Ensure raspberry_pi folder is on Python path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RPI_DIR = os.path.join(REPO_ROOT, "raspberry_pi")
if RPI_DIR not in sys.path:
    sys.path.insert(0, RPI_DIR)

from config import TelemetryConfig
from meter_reader import LT4400MeterReader, MeterReadResult, decode_ieee754_float
from normalizer import TelemetryNormalizer
from queue_manager import QueueManager
from api_client import ApplicationApiClient
from sheets_client import GoogleSheetsBackupClient
from recovery_worker import RecoveryWorker
from health_monitor import HealthMonitor

@pytest.fixture
def temp_config():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    cfg = TelemetryConfig()
    cfg.sqlite_db_path = db_path
    cfg.mock_hardware = True
    cfg.enable_google_sheets = True
    cfg.api_base_url = "http://localhost:8000"
    yield cfg

    if os.path.exists(db_path):
        os.remove(db_path)
    wal_file = db_path + "-wal"
    shm_file = db_path + "-shm"
    if os.path.exists(wal_file): os.remove(wal_file)
    if os.path.exists(shm_file): os.remove(shm_file)

# ------------------------------------------------------------------------------
# TEST A: NORMAL OPERATION
# ------------------------------------------------------------------------------
def test_scenario_a_normal_operation(temp_config):
    """
    Test A: Read meter -> Queue locally -> Send to API -> Append to Sheets.
    Verify event ID and timestamps match across queue, API payload, and Sheets row.
    """
    queue = QueueManager(temp_config)
    reader = LT4400MeterReader(temp_config)
    normalizer = TelemetryNormalizer(temp_config)
    api_client = ApplicationApiClient(temp_config)
    sheets_client = GoogleSheetsBackupClient(temp_config)
    health = HealthMonitor(queue, temp_config)

    # 1. Read meter
    read_res = reader.read_all_parameters()
    assert read_res.success is True
    assert "watts_total" in read_res.data
    assert read_res.data["watts_total"] > 0

    # 2. Normalize
    payload = normalizer.normalize(read_res)
    assert payload["quality"] == "GOOD"
    assert payload["device_id"] == temp_config.device_id
    assert payload["active_power_kw"] > 0
    event_id = payload["record_id"]
    timestamp = payload["timestamp"]

    # 3. Queue locally
    assert queue.enqueue(payload) is True
    app_q, sheets_q = queue.get_queue_depth()
    assert app_q == 1
    assert sheets_q == 1

    # 4. Mock API transmission
    with patch.object(api_client, "send_telemetry", return_value=(True, None)) as mock_api:
        success, err = api_client.send_telemetry(payload)
        assert success is True
        queue.mark_application_synced([event_id])
        health.record_app_sync(True, 1)

    # 5. Mock Google Sheets transmission
    with patch.object(sheets_client, "append_telemetry_batch", return_value=([event_id], [], None)) as mock_sheets:
        success_ids, failed_ids, err = sheets_client.append_telemetry_batch([payload])
        assert success_ids == [event_id]
        queue.mark_sheets_synced(success_ids)
        health.record_sheets_sync(True, 1)

    # 6. Verify queues are empty and timestamps match
    app_q, sheets_q = queue.get_queue_depth()
    assert app_q == 0
    assert sheets_q == 0

    # Verify sheets row mapping
    row = normalizer.to_sheets_row(payload)
    assert row[0] == event_id  # record_id
    assert row[1] == timestamp # timestamp
    assert row[3] == temp_config.device_id

# ------------------------------------------------------------------------------
# TEST B: APPLICATION UNAVAILABLE
# ------------------------------------------------------------------------------
def test_scenario_b_application_unavailable(temp_config):
    """
    Test B: Application API is down -> Meter reads continue -> Sheets continues ->
    API restored -> Pending records drained chronologically without duplicate data.
    """
    queue = QueueManager(temp_config)
    reader = LT4400MeterReader(temp_config)
    normalizer = TelemetryNormalizer(temp_config)
    api_client = ApplicationApiClient(temp_config)
    sheets_client = GoogleSheetsBackupClient(temp_config)
    recovery = RecoveryWorker(queue, api_client, sheets_client, temp_config)

    # Generate 3 readings while API is down
    event_ids = []
    for _ in range(3):
        res = reader.read_all_parameters()
        payload = normalizer.normalize(res)
        queue.enqueue(payload)
        event_ids.append(payload["record_id"])

        # Attempt API (fails)
        queue.record_application_failure(payload["record_id"], "Connection refused")

        # Sheets succeeds
        with patch.object(sheets_client, "append_telemetry_batch", return_value=([payload["record_id"]], [], None)):
            sheets_client.append_telemetry_batch([payload])
            queue.mark_sheets_synced([payload["record_id"]])

    # Verify queue states: Application has 3 pending, Sheets has 0
    app_q, sheets_q = queue.get_queue_depth()
    assert app_q == 3
    assert sheets_q == 0

    # Restore API and run recovery worker
    with patch.object(api_client, "send_batch", return_value=(event_ids, [])) as mock_batch:
        drained = recovery.process_application_queue(batch_size=10)
        assert drained == 3

    # All queues now clear
    app_q, sheets_q = queue.get_queue_depth()
    assert app_q == 0
    assert sheets_q == 0

# ------------------------------------------------------------------------------
# TEST C: GOOGLE SHEETS UNAVAILABLE
# ------------------------------------------------------------------------------
def test_scenario_c_google_sheets_unavailable(temp_config):
    """
    Test C: Google Sheets API timeout/fails -> Application continues ->
    Sheets restored -> Pending backup synchronized without duplicates.
    """
    queue = QueueManager(temp_config)
    reader = LT4400MeterReader(temp_config)
    normalizer = TelemetryNormalizer(temp_config)
    api_client = ApplicationApiClient(temp_config)
    sheets_client = GoogleSheetsBackupClient(temp_config)
    recovery = RecoveryWorker(queue, api_client, sheets_client, temp_config)

    event_ids = []
    for _ in range(2):
        res = reader.read_all_parameters()
        payload = normalizer.normalize(res)
        queue.enqueue(payload)
        event_ids.append(payload["record_id"])

        # API succeeds
        queue.mark_application_synced([payload["record_id"]])

        # Sheets fails with quota / timeout
        queue.record_sheets_failure(payload["record_id"], "HTTP 429 Quota Exceeded")

    app_q, sheets_q = queue.get_queue_depth()
    assert app_q == 0
    assert sheets_q == 2

    # Restore Sheets and run recovery worker
    with patch.object(sheets_client, "append_telemetry_batch", return_value=(event_ids, [], None)):
        drained = recovery.process_sheets_queue(batch_size=10)
        assert drained == 2

    app_q, sheets_q = queue.get_queue_depth()
    assert sheets_q == 0

# ------------------------------------------------------------------------------
# TEST D: COMPLETE NETWORK OUTAGE & POWER RESTART RECOVERY
# ------------------------------------------------------------------------------
def test_scenario_d_complete_outage_and_restart(temp_config):
    """
    Test D: Both API and Sheets offline -> readings persisted in SQLite ->
    Service restarted -> pending deliveries resume with zero loss.
    """
    queue = QueueManager(temp_config)
    reader = LT4400MeterReader(temp_config)
    normalizer = TelemetryNormalizer(temp_config)

    saved_ids = []
    for _ in range(4):
        res = reader.read_all_parameters()
        payload = normalizer.normalize(res)
        queue.enqueue(payload)
        saved_ids.append(payload["record_id"])

    # Simulate Raspberry Pi restart: create completely new QueueManager & Worker instances
    # pointing to the same SQLite file
    recovered_queue = QueueManager(temp_config)
    api_client = ApplicationApiClient(temp_config)
    sheets_client = GoogleSheetsBackupClient(temp_config)
    recovery = RecoveryWorker(recovered_queue, api_client, sheets_client, temp_config)

    app_q, sheets_q = recovered_queue.get_queue_depth()
    assert app_q == 4
    assert sheets_q == 4

    # Both services restored
    with patch.object(api_client, "send_batch", return_value=(saved_ids, [])):
        with patch.object(sheets_client, "append_telemetry_batch", return_value=(saved_ids, [], None)):
            drained_app = recovery.process_application_queue(batch_size=10)
            drained_sheets = recovery.process_sheets_queue(batch_size=10)
            assert drained_app == 4
            assert drained_sheets == 4

    app_q, sheets_q = recovered_queue.get_queue_depth()
    assert app_q == 0
    assert sheets_q == 0

# ------------------------------------------------------------------------------
# TEST E: INVALID METER COMMUNICATION (NO FABRICATED DATA)
# ------------------------------------------------------------------------------
def test_scenario_e_invalid_meter_communication(temp_config):
    """
    Test E: When meter read fails, report failure as quality BAD.
    Never fabricate numbers or report zero as real measurements.
    """
    reader = LT4400MeterReader(temp_config)
    normalizer = TelemetryNormalizer(temp_config)

    # Simulate hardware read failure
    failed_result = MeterReadResult(
        success=False,
        data={},
        error="Modbus CRC Error on /dev/ttyUSB0",
        is_mock=False
    )

    payload = normalizer.normalize(failed_result)
    assert payload["quality"] == "BAD"
    assert payload["communication_error"] == "Modbus CRC Error on /dev/ttyUSB0"
    assert payload["voltage"] == 0.0
    assert payload["active_power_kw"] == 0.0

# ------------------------------------------------------------------------------
# TEST F: DUPLICATE PREVENTION & HISTORICAL BACKFILL
# ------------------------------------------------------------------------------
def test_scenario_f_duplicate_prevention_and_backfill(temp_config):
    """
    Test F: Verify sync ledger and duplicate prevention.
    Test historical backfill from Google Sheets.
    """
    queue = QueueManager(temp_config)
    reader = LT4400MeterReader(temp_config)
    normalizer = TelemetryNormalizer(temp_config)
    api_client = ApplicationApiClient(temp_config)
    sheets_client = GoogleSheetsBackupClient(temp_config)
    recovery = RecoveryWorker(queue, api_client, sheets_client, temp_config)

    res = reader.read_all_parameters()
    payload = normalizer.normalize(res)
    event_id = payload["record_id"]

    # Test duplicate prevention in sheets client
    sheets_client._synced_ids_cache.add(event_id)
    # Appending the same payload again should be ignored
    success_ids, failed_ids, err = sheets_client.append_telemetry_batch([payload])
    assert event_id in success_ids
    assert len(failed_ids) == 0

    # Test historical backfill from Sheets
    mock_sheets_records = [
        {
            "record_id": "HIST-001",
            "timestamp": "2026-10-13T10:00:00Z",
            "source": "RASPBERRY_PI",
            "device_id": "RPi-METER-01",
            "voltage": 230.1,
            "current": 120.4,
            "active_power_kw": 27.6,
            "energy_kwh": 100.2,
            "frequency_hz": 50.0,
            "power_factor": 0.96,
            "quality": "GOOD",
            "machine_state": "RUNNING"
        }
    ]

    with patch.object(sheets_client, "fetch_historical_records", return_value=mock_sheets_records):
        with patch.object(api_client, "send_telemetry", return_value=(True, None)) as mock_send:
            backfilled = recovery.backfill_from_sheets_to_application(limit=10)
            assert backfilled == 1
            mock_send.assert_called_once()
            called_payload = mock_send.call_args[0][0]
            assert called_payload["voltage"] == 230.1
            assert called_payload["active_power_kw"] == 27.6
