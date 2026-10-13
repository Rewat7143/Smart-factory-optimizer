"""
Hardware Adapters for Factory Energy Autopilot Edge Telemetry.

Isolates all hardware-specific Modbus communication and GPIO operations
so that high-level telemetry processing, API sync, Google Sheets backup,
and relay state-machine logic remain strictly hardware-independent.

Today: Verified Raspberry Pi 4B adapter (RS-485 Modbus RTU + RPi GPIO).
Tomorrow: Arduino UNO Q adapter (serial stream / bridge / MCU GPIO).
"""

import time
import struct
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, NamedTuple
from config import TelemetryConfig, config as default_config

logger = logging.getLogger("HardwareAdapters")

try:
    import minimalmodbus
    import serial
    MODBUS_LIB_AVAILABLE = True
except ImportError:
    minimalmodbus = None
    serial = None
    MODBUS_LIB_AVAILABLE = False

try:
    import RPi.GPIO as GPIO
    RPI_GPIO_AVAILABLE = True
except ImportError:
    GPIO = None
    RPI_GPIO_AVAILABLE = False


class MeterReadResult(NamedTuple):
    success: bool
    data: Dict[str, Any]
    error: Optional[str]
    is_mock: bool


import math

def decode_ieee754_float(high_word: int, low_word: int) -> float:
    """
    Decodes two 16-bit Modbus registers into an IEEE-754 32-bit float.
    L&T WL 4400 uses word-swapped (little-endian word order / CDAB) IEEE-754 single precision float.
    """
    try:
        raw_bytes = struct.pack(">HH", low_word, high_word)
        val = struct.unpack(">f", raw_bytes)[0]
        if math.isnan(val) or math.isinf(val) or abs(val) > 1e12:
            return 0.0
        return val
    except Exception:
        return 0.0



# ==============================================================================
# METER HARDWARE ADAPTERS
# ==============================================================================

class BaseMeterAdapter(ABC):
    """Abstract interface for energy meter acquisition hardware."""

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the physical acquisition bus."""
        pass

    @abstractmethod
    def read_all_parameters(self) -> MeterReadResult:
        """Read all electrical parameters. Never invent or falsify data on failure."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Safely release the physical serial/bus interface."""
        pass


class RaspberryPi4BMeterAdapter(BaseMeterAdapter):
    """
    Hardware adapter for Raspberry Pi 4B connected to L&T WL 4400 Multi-Function Meter
    via RS-485 Modbus RTU (USB-RS485 dongle or UART GPIO shield).
    """

    METER_REGISTERS = {
        "watts_total": (100, 101),
        "watts_r": (102, 103),
        "watts_y": (104, 105),
        "watts_b": (106, 107),
        "pf_avg": (116, 117),
        "pf_r": (118, 119),
        "pf_y": (120, 121),
        "pf_b": (122, 123),
        "va_total": (124, 125),
        "va_r": (126, 127),
        "va_y": (128, 129),
        "va_b": (130, 131),
        "v_ll_avg": (132, 133),
        "v_ry": (134, 135),
        "v_yb": (136, 137),
        "v_br": (138, 139),
        "v_ln_avg": (140, 141),
        "v_r": (142, 143),
        "v_y": (144, 145),
        "v_b": (146, 147),
        "current_total": (148, 149),
        "current_r": (150, 151),
        "current_y": (152, 153),
        "current_b": (154, 155),
        "frequency": (156, 157),
        "energy_wh": (158, 159),
        "energy_vah": (160, 161),
        "load_hours": (162, 163)
    }

    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or default_config
        self.instrument = None
        self._mock_accum_wh = 175131297.0
        self._mock_accum_vah = 193873100.0

    def connect(self) -> bool:
        if self.config.mock_hardware:
            logger.info("[RPi4B Adapter] Running in MOCK_HARDWARE mode.")
            return True

        if not MODBUS_LIB_AVAILABLE:
            logger.error("[RPi4B Adapter] minimalmodbus/pyserial not installed.")
            return False

        try:
            parity_val = serial.PARITY_EVEN
            if self.config.parity == "NONE":
                parity_val = serial.PARITY_NONE
            elif self.config.parity == "ODD":
                parity_val = serial.PARITY_ODD

            inst = minimalmodbus.Instrument(self.config.serial_port, self.config.meter_id)
            inst.serial.baudrate = self.config.baudrate
            inst.serial.bytesize = self.config.bytesize
            inst.serial.parity = parity_val
            inst.serial.stopbits = self.config.stopbits
            inst.serial.timeout = self.config.timeout_seconds
            inst.mode = minimalmodbus.MODE_RTU
            inst.clear_buffers_before_each_transaction = True

            self.instrument = inst
            logger.info(
                f"[RPi4B Adapter] Connected to RS-485 port {self.config.serial_port} "
                f"(ID: {self.config.meter_id}, {self.config.baudrate} baud, Parity: {self.config.parity})"
            )
            return True
        except Exception as e:
            logger.error(f"[RPi4B Adapter] Failed to open {self.config.serial_port}: {e}")
            self.instrument = None
            return False

    def read_all_parameters(self) -> MeterReadResult:
        if self.config.mock_hardware:
            return self._mock_reading()

        if self.instrument is None:
            if not self.connect():
                return MeterReadResult(
                    success=False,
                    data={},
                    error=f"Serial port {self.config.serial_port} unavailable",
                    is_mock=False
                )

        raw_values = {}
        try:
            # Block read (PDU registers 100 to 163 = 64 holding registers)
            block = self.instrument.read_registers(100, 64, functioncode=3)
            for param, (r1, r2) in self.METER_REGISTERS.items():
                i1, i2 = r1 - 100, r2 - 100
                if 0 <= i1 < len(block) and 0 <= i2 < len(block):
                    raw_values[param] = round(decode_ieee754_float(block[i1], block[i2]), 4)

            # In 3P4W mode, if line-to-line registers are zero, calculate from line-to-neutral
            v_ln = raw_values.get("v_ln_avg", 0.0)
            if v_ln > 50.0 and raw_values.get("v_ll_avg", 0.0) < 10.0:
                raw_values["v_ll_avg"] = round(v_ln * 1.73205, 2)
                raw_values["v_ry"] = round(raw_values.get("v_r", v_ln) * 1.73205, 2)
                raw_values["v_yb"] = round(raw_values.get("v_y", v_ln) * 1.73205, 2)
                raw_values["v_br"] = round(raw_values.get("v_b", v_ln) * 1.73205, 2)

            return MeterReadResult(success=True, data=raw_values, error=None, is_mock=False)
        except Exception as e:
            logger.error(f"[RPi4B Adapter] Modbus read error: {e}")
            return MeterReadResult(success=False, data={}, error=str(e), is_mock=False)

    def disconnect(self) -> None:
        if self.instrument and hasattr(self.instrument, "serial") and self.instrument.serial:
            try:
                self.instrument.serial.close()
            except Exception:
                pass
        self.instrument = None

    def _mock_reading(self) -> MeterReadResult:
        """Deterministic test reading used solely during automated testing."""
        return MeterReadResult(
            success=True,
            data={
                "watts_total": 78500.0,
                "watts_r": 26200.0,
                "watts_y": 26100.0,
                "watts_b": 26200.0,
                "pf_avg": 0.965,
                "pf_r": 0.964,
                "pf_y": 0.966,
                "pf_b": 0.965,
                "va_total": 81347.0,
                "va_r": 27178.0,
                "va_y": 27018.0,
                "va_b": 27150.0,
                "v_ll_avg": 399.2,
                "v_ry": 399.5,
                "v_yb": 398.9,
                "v_br": 399.2,
                "v_ln_avg": 230.5,
                "v_r": 230.7,
                "v_y": 230.3,
                "v_b": 230.5,
                "current_total": 113.6,
                "current_r": 37.8,
                "current_y": 37.9,
                "current_b": 37.9,
                "frequency": 50.02,
                "energy_wh": self._mock_accum_wh,
                "energy_vah": self._mock_accum_vah,
                "load_hours": 1420.5
            },
            error=None,
            is_mock=True
        )


class ArduinoUnoQMeterAdapter(BaseMeterAdapter):
    """
    Adapter skeleton for tomorrow's Arduino UNO Q migration.
    UNO Q topology:
      - Embedded MCU reads L&T Modbus over RS-485 shield.
      - Transmits formatted JSON telemetry lines over USB CDC Serial (/dev/ttyACM0).
      - Alternatively, if UNO Q runs a Linux/MicroPython core, it executes the Modbus engine.
    """

    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or default_config
        self.serial_conn = None

    def connect(self) -> bool:
        logger.info(
            f"[Arduino UNO Q Adapter] Preparing connection on {self.config.serial_port}. "
            "Requires UNO Q edge firmware loaded and RS-485 shield attached."
        )
        if self.config.mock_hardware:
            return True
        if not serial:
            logger.error("[Arduino UNO Q Adapter] pyserial not available.")
            return False
        try:
            self.serial_conn = serial.Serial(self.config.serial_port, 115200, timeout=self.config.timeout_seconds)
            return True
        except Exception as e:
            logger.error(f"[Arduino UNO Q Adapter] Connection failed: {e}")
            return False

    def read_all_parameters(self) -> MeterReadResult:
        if self.config.mock_hardware:
            return RaspberryPi4BMeterAdapter(self.config)._mock_reading()

        if not self.serial_conn:
            if not self.connect():
                return MeterReadResult(success=False, data={}, error="UNO Q serial disconnected", is_mock=False)

        try:
            # Poll or read JSON frame from UNO Q firmware
            line = self.serial_conn.readline().decode("utf-8").strip()
            if not line:
                return MeterReadResult(success=False, data={}, error="UNO Q timeout: No data received", is_mock=False)
            import json
            data = json.loads(line)
            return MeterReadResult(success=True, data=data, error=None, is_mock=False)
        except Exception as e:
            return MeterReadResult(success=False, data={}, error=f"UNO Q parsing error: {e}", is_mock=False)

    def disconnect(self) -> None:
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except Exception:
                pass
        self.serial_conn = None


# ==============================================================================
# RELAY HARDWARE ADAPTERS
# ==============================================================================

class BaseRelayAdapter(ABC):
    """Abstract interface for 3-channel relay control hardware."""

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize GPIO or peripheral output states."""
        pass

    @abstractmethod
    def set_relay(self, channel: int, state: bool) -> bool:
        """
        Command relay channel (1, 2, or 3).
        state=True: Relay commanded to shed/active state.
        state=False: Relay commanded to normal/de-energized state.
        """
        pass

    @abstractmethod
    def get_relay_state(self, channel: int) -> bool:
        """Get the current tracked state of relay channel (1, 2, or 3)."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Safely reset all relays and release hardware resources."""
        pass


class RaspberryPi4BRelayAdapter(BaseRelayAdapter):
    """
    Physical GPIO relay adapter for Raspberry Pi 4B.
    Strict safety rule: Runs in MONITOR_ONLY mode unless explicitly configured otherwise.
    Does NOT invent GPIO pins or relay polarity.
    """

    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or default_config
        self.pins = {
            1: self.config.relay_1_pin,
            2: self.config.relay_2_pin,
            3: self.config.relay_3_pin
        }
        self.active_low = self.config.relay_active_low
        self.monitor_only = self.config.relay_monitor_only
        self.states = {1: False, 2: False, 3: False}
        self._gpio_initialized = False

    def initialize(self) -> bool:
        configured_pins = [p for p in self.pins.values() if p is not None]
        if not configured_pins:
            logger.info(
                "[RPi4B Relay Adapter] No GPIO pins configured in environment (RELAY_1_PIN, etc.). "
                "Operating in safe virtual MONITOR_ONLY mode."
            )
            return True

        if self.monitor_only:
            logger.info(
                f"[RPi4B Relay Adapter] Configured pins: {self.pins}. "
                "SAFETY INTERLOCK: RELAY_MODE is MONITOR_ONLY. Physical GPIOs will not be driven."
            )
            return True

        if not RPI_GPIO_AVAILABLE:
            logger.warning(
                "[RPi4B Relay Adapter] RPi.GPIO library not available. "
                "Falling back to virtual relay tracking."
            )
            return True

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            for ch, pin in self.pins.items():
                if pin is not None:
                    # Initial operating state: relays energized / contacts closed (active-low: LOW = on)
                    init_level = GPIO.LOW if self.active_low else GPIO.HIGH
                    GPIO.setup(pin, GPIO.OUT, initial=init_level)
                    logger.info(f"[RPi4B Relay Adapter] Relay channel {ch} setup on BCM GPIO {pin} (initially energized/ON).")
            self._gpio_initialized = True
            return True
        except Exception as e:
            logger.error(f"[RPi4B Relay Adapter] GPIO initialization failed: {e}")
            return False

    def set_relay(self, channel: int, state: bool) -> bool:
        if channel not in (1, 2, 3):
            logger.error(f"Invalid relay channel {channel}. Valid channels are 1, 2, 3.")
            return False

        self.states[channel] = state
        pin = self.pins.get(channel)

        if self.monitor_only or pin is None or not self._gpio_initialized:
            # Virtual/monitor-only mode: record state and log
            action_desc = "SHED (OFF / DISCONNECTED)" if state else "RESTORED (ON / CONNECTED)"
            logger.info(
                f"[MONITOR_ONLY] Relay channel {channel} {action_desc}. "
                f"Physical pin {pin} unactuated."
            )
            return True

        # Active hardware actuation:
        # state == True -> SHED (Turn OFF load) -> active-low: GPIO.HIGH (de-energize coil)
        # state == False -> RESTORE (Turn ON load) -> active-low: GPIO.LOW (energize coil)
        try:
            if self.active_low:
                level = GPIO.HIGH if state else GPIO.LOW
            else:
                level = GPIO.LOW if state else GPIO.HIGH

            GPIO.output(pin, level)
            logger.info(
                f"[RPi4B Relay Adapter] Actuated Relay {channel} (BCM {pin}) -> Level "
                f"{'HIGH (3.3V)' if level == GPIO.HIGH else 'LOW (0V)'} (Load {'SHED/OFF' if state else 'RESTORED/ON'}, Active-Low={self.active_low})."
            )
            return True
        except Exception as e:
            logger.error(f"[RPi4B Relay Adapter] Failed to actuate Relay {channel}: {e}")
            return False

    def set_polarity(self, active_low: bool) -> None:
        """Dynamically update relay trigger polarity without service restart."""
        self.active_low = active_low
        logger.info(f"[RPi4B Relay Adapter] Polarity updated: Active-Low={self.active_low}")
        if self._gpio_initialized and not self.monitor_only:
            for ch, state in self.states.items():
                self.set_relay(ch, state)

    def test_pulse(self, cycles: int = 3) -> None:
        """Rapidly toggles all configured relays so the user can visually verify LEDs and hear clicks."""
        if not self._gpio_initialized or self.monitor_only or not RPI_GPIO_AVAILABLE:
            logger.warning("[RPi4B Relay Adapter] Cannot run test pulse: GPIO not initialized or in monitor-only mode.")
            return

        import time
        logger.info("[RPi4B Relay Adapter] Executing diagnostic test pulse on all relay pins...")
        try:
            for i in range(cycles):
                # Cycle LOW (0V)
                for ch, pin in self.pins.items():
                    if pin is not None:
                        GPIO.setup(pin, GPIO.OUT)
                        GPIO.output(pin, GPIO.LOW)
                time.sleep(0.4)

                # Cycle HIGH (3.3V)
                for ch, pin in self.pins.items():
                    if pin is not None:
                        GPIO.setup(pin, GPIO.OUT)
                        GPIO.output(pin, GPIO.HIGH)
                time.sleep(0.4)

            # Re-apply tracked state
            for ch, state in self.states.items():
                self.set_relay(ch, state)
            logger.info("[RPi4B Relay Adapter] Diagnostic test pulse finished successfully.")
        except Exception as e:
            logger.error(f"[RPi4B Relay Adapter] Error during test pulse: {e}")

    def get_relay_state(self, channel: int) -> bool:
        return self.states.get(channel, False)

    def cleanup(self) -> None:
        if self._gpio_initialized and RPI_GPIO_AVAILABLE:
            try:
                # Reset all configured pins to safe de-energized state
                for pin in self.pins.values():
                    if pin is not None:
                        safe_level = GPIO.HIGH if self.active_low else GPIO.LOW
                        GPIO.output(pin, safe_level)
                GPIO.cleanup()
                logger.info("[RPi4B Relay Adapter] GPIO pins reset to safe de-energized state.")
            except Exception as e:
                logger.error(f"[RPi4B Relay Adapter] Cleanup error: {e}")
        self._gpio_initialized = False


class ArduinoUnoQRelayAdapter(BaseRelayAdapter):
    """
    Adapter skeleton for tomorrow's Arduino UNO Q migration.
    Commands digital output pins or industrial relay shields on UNO Q via serial protocol.
    """

    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or default_config
        self.states = {1: False, 2: False, 3: False}
        self.serial_conn = None

    def initialize(self) -> bool:
        logger.info("[Arduino UNO Q Relay Adapter] Initializing virtual UNO Q relay channels.")
        return True

    def set_relay(self, channel: int, state: bool) -> bool:
        if channel not in (1, 2, 3):
            return False
        self.states[channel] = state
        logger.info(f"[Arduino UNO Q Relay Adapter] Channel {channel} -> state {state} (queued for UNO Q bridge).")
        return True

    def get_relay_state(self, channel: int) -> bool:
        return self.states.get(channel, False)

    def cleanup(self) -> None:
        self.states = {1: False, 2: False, 3: False}


class VirtualRelayAdapter(BaseRelayAdapter):
    """In-memory virtual relay adapter for testing and simulation."""

    def __init__(self):
        self.states = {1: False, 2: False, 3: False}

    def initialize(self) -> bool:
        return True

    def set_relay(self, channel: int, state: bool) -> bool:
        if channel in (1, 2, 3):
            self.states[channel] = state
            return True
        return False

    def get_relay_state(self, channel: int) -> bool:
        return self.states.get(channel, False)

    def cleanup(self) -> None:
        self.states = {1: False, 2: False, 3: False}


# ==============================================================================
# ADAPTER FACTORY
# ==============================================================================

def create_meter_adapter(config: Optional[TelemetryConfig] = None) -> BaseMeterAdapter:
    """Instantiate the appropriate meter adapter based on configuration."""
    cfg = config or default_config
    platform = cfg.hardware_platform.upper()
    if platform == "UNO_Q":
        return ArduinoUnoQMeterAdapter(cfg)
    return RaspberryPi4BMeterAdapter(cfg)


def create_relay_adapter(config: Optional[TelemetryConfig] = None) -> BaseRelayAdapter:
    """Instantiate the appropriate relay adapter based on configuration."""
    cfg = config or default_config
    platform = cfg.hardware_platform.upper()
    if platform == "UNO_Q":
        return ArduinoUnoQRelayAdapter(cfg)
    if platform == "VIRTUAL":
        return VirtualRelayAdapter()
    return RaspberryPi4BRelayAdapter(cfg)
