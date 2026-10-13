import os
import sys
import tempfile
import pytest
from unittest.mock import MagicMock, patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RPI_DIR = os.path.join(REPO_ROOT, "raspberry_pi")
if RPI_DIR not in sys.path:
    sys.path.insert(0, RPI_DIR)

from config import TelemetryConfig
from hardware_adapters import (
    BaseMeterAdapter,
    BaseRelayAdapter,
    RaspberryPi4BMeterAdapter,
    ArduinoUnoQMeterAdapter,
    RaspberryPi4BRelayAdapter,
    ArduinoUnoQRelayAdapter,
    VirtualRelayAdapter,
    create_meter_adapter,
    create_relay_adapter
)
from relay_control import RelayController, RelayState
import importlib.util
rpi_main_spec = importlib.util.spec_from_file_location("rpi_main", os.path.join(RPI_DIR, "main.py"))
rpi_main = importlib.util.module_from_spec(rpi_main_spec)
rpi_main_spec.loader.exec_module(rpi_main)
TelemetryService = rpi_main.TelemetryService


@pytest.fixture
def test_config():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    cfg = TelemetryConfig()
    cfg.sqlite_db_path = db_path
    cfg.mock_hardware = True
    cfg.enable_google_sheets = False
    cfg.peak_demand_threshold_kw = 80.0
    cfg.warning_threshold_ratio = 0.90
    cfg.restore_hysteresis_kw = 5.0
    cfg.min_trip_time_seconds = 0.1
    cfg.min_restart_delay_seconds = 0.1
    yield cfg
    if os.path.exists(db_path):
        os.remove(db_path)


# ------------------------------------------------------------------------------
# 1. HARDWARE ADAPTER TESTS
# ------------------------------------------------------------------------------
def test_hardware_adapter_factory(test_config):
    # RPi platform
    test_config.hardware_platform = "RPI4B"
    meter = create_meter_adapter(test_config)
    relay = create_relay_adapter(test_config)
    assert isinstance(meter, RaspberryPi4BMeterAdapter)
    assert isinstance(relay, RaspberryPi4BRelayAdapter)

    # UNO Q platform
    test_config.hardware_platform = "UNO_Q"
    meter_uno = create_meter_adapter(test_config)
    relay_uno = create_relay_adapter(test_config)
    assert isinstance(meter_uno, ArduinoUnoQMeterAdapter)
    assert isinstance(relay_uno, ArduinoUnoQRelayAdapter)

    # Virtual platform
    test_config.hardware_platform = "VIRTUAL"
    relay_virt = create_relay_adapter(test_config)
    assert isinstance(relay_virt, VirtualRelayAdapter)


def test_rpi_meter_adapter_mock_readings(test_config):
    adapter = RaspberryPi4BMeterAdapter(test_config)
    assert adapter.connect() is True
    res = adapter.read_all_parameters()
    assert res.success is True
    assert res.data["watts_total"] > 0
    assert "pf_avg" in res.data
    assert "v_ll_avg" in res.data
    assert "frequency" in res.data


def test_uno_q_meter_adapter_interface(test_config):
    adapter = ArduinoUnoQMeterAdapter(test_config)
    assert adapter.connect() is True
    res = adapter.read_all_parameters()
    assert res.success is True
    assert res.data["watts_total"] > 0


# ------------------------------------------------------------------------------
# 2. RELAY CONTROLLER & 3-RELAY PEAK DEMAND STATE MACHINE
# ------------------------------------------------------------------------------
def test_relay_controller_monitor_only_by_default(test_config):
    """Verify relay controller strictly enforces MONITOR_ONLY mode by default."""
    virt_adapter = VirtualRelayAdapter()
    ctrl = RelayController(adapter=virt_adapter, config=test_config)
    assert ctrl.monitor_only is True

    # High demand should advance state machine but indicate monitor mode
    rep = ctrl.evaluate_demand(95.0, current_time=100.0)
    assert rep["state"] == RelayState.STAGE_1_SHED
    assert rep["mode"] == "MONITOR_ONLY"
    assert rep["action_taken"] == "SHED_CH1"
    assert rep["channels"][1]["is_shed"] is True


def test_relay_controller_unconfigured_threshold_handling():
    """Verify that when no peak threshold is configured, controller stays safe."""
    cfg = TelemetryConfig()
    cfg.peak_demand_threshold_kw = None
    virt_adapter = VirtualRelayAdapter()
    ctrl = RelayController(adapter=virt_adapter, config=cfg)

    # Even with very high demand, it should not invent a threshold
    rep = ctrl.evaluate_demand(500.0, current_time=100.0)
    assert rep["state"] == RelayState.NORMAL
    assert rep["action_taken"] == "NONE"
    assert rep["channels"][1]["is_shed"] is False


def test_relay_controller_sequential_shed_and_restore_cycle(test_config):
    """
    Test complete lifecycle:
    Normal -> Warning -> Stage 1 Shed -> Stage 2 Shed -> Restoring -> Normal
    """
    virt_adapter = VirtualRelayAdapter()
    ctrl = RelayController(adapter=virt_adapter, config=test_config)
    t = 1000.0

    # 1. Demand below warning (60 kW <= 72 kW)
    r1 = ctrl.evaluate_demand(60.0, current_time=t)
    assert r1["state"] == RelayState.NORMAL

    # 2. Demand in warning band (75 kW > 72 kW and <= 80 kW)
    t += 1.0
    r2 = ctrl.evaluate_demand(75.0, current_time=t)
    assert r2["state"] == RelayState.WARNING
    assert r2["warning"] is True

    # 3. Demand exceeds threshold (85 kW > 80 kW) -> Stage 1 Shed (Relay 1)
    t += 1.0
    r3 = ctrl.evaluate_demand(85.0, current_time=t)
    assert r3["state"] == RelayState.STAGE_1_SHED
    assert r3["action_taken"] == "SHED_CH1"
    assert ctrl.channels[1].is_shed is True
    assert ctrl.channels[2].is_shed is False

    # 4. Demand remains high after dwell time -> Stage 2 Shed (Relay 2)
    t += test_config.min_trip_time_seconds + 0.1
    r4 = ctrl.evaluate_demand(86.0, current_time=t)
    assert r4["state"] == RelayState.STAGE_2_SHED
    assert r4["action_taken"] == "SHED_CH2"
    assert ctrl.channels[2].is_shed is True

    # 5. Demand drops below restore threshold (70 kW <= 75 kW) -> Sequential restore
    t += test_config.min_trip_time_seconds + 0.1
    r5 = ctrl.evaluate_demand(70.0, current_time=t)
    assert r5["state"] == RelayState.RESTORING
    # Highest priority shed load (Ch 2) is restored first
    assert r5["action_taken"] == "RESTORE_CH2"
    assert ctrl.channels[2].is_shed is False
    assert ctrl.channels[1].is_shed is True

    # 6. Anti-inrush delay elapses, next channel restored
    t += test_config.min_restart_delay_seconds + 0.1
    r6 = ctrl.evaluate_demand(70.0, current_time=t)
    assert r6["action_taken"] == "RESTORE_CH1"
    assert ctrl.channels[1].is_shed is False

    # 7. Fully restored -> NORMAL
    t += 1.0
    r7 = ctrl.evaluate_demand(70.0, current_time=t)
    assert r7["state"] == RelayState.NORMAL


def test_relay_emergency_restore(test_config):
    virt_adapter = VirtualRelayAdapter()
    ctrl = RelayController(adapter=virt_adapter, config=test_config)
    ctrl.evaluate_demand(95.0, current_time=100.0)
    assert ctrl.channels[1].is_shed is True

    ctrl.emergency_restore_all()
    assert ctrl.channels[1].is_shed is False
    assert ctrl.current_state == RelayState.NORMAL


# ------------------------------------------------------------------------------
# 3. TELEMETRY SERVICE INITIALIZATION & SINGLE ITERATION
# ------------------------------------------------------------------------------
def test_main_telemetry_service_iteration(test_config):
    service = TelemetryService(config=test_config, monitor_only=True)
    with patch.object(service.api_client, "send_telemetry", return_value=(True, None)):
        service._iteration()

    # Verify queue was populated and marked synced
    app_q, sheets_q = service.queue.get_queue_depth()
    assert app_q == 0
    service._shutdown()
