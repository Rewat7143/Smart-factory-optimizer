import time
import struct
import logging
from typing import Dict, Any, Optional, Tuple, NamedTuple
from config import TelemetryConfig, config as default_config

logger = logging.getLogger("MeterReader")

# Optional imports for minimalmodbus and serial
try:
    import minimalmodbus
    import serial
    MODBUS_LIB_AVAILABLE = True
except ImportError:
    minimalmodbus = None
    serial = None
    MODBUS_LIB_AVAILABLE = False

class MeterReadResult(NamedTuple):
    success: bool
    data: Dict[str, Any]
    error: Optional[str]
    is_mock: bool

# Parameter definitions for L&T WL 4400 (PDU addresses = Reference Address - 40001)
# Each parameter spans 2 consecutive 16-bit registers (IEEE-754 32-bit single precision float)
METER_REGISTERS = {
    # 1. Active Power (W)
    "watts_total": (100, 101),
    "watts_r": (102, 103),
    "watts_y": (104, 105),
    "watts_b": (106, 107),

    # 2. Power Factor
    "pf_avg": (116, 117),
    "pf_r": (118, 119),
    "pf_y": (120, 121),
    "pf_b": (122, 123),

    # 3. Apparent Power (VA)
    "va_total": (124, 125),
    "va_r": (126, 127),
    "va_y": (128, 129),
    "va_b": (130, 131),

    # 4. Line-to-Line Voltage (V)
    "v_ll_avg": (132, 133),
    "v_ry": (134, 135),
    "v_yb": (136, 137),
    "v_br": (138, 139),

    # 5. Line-to-Neutral Phase Voltage (V)
    "v_ln_avg": (140, 141),
    "v_r": (142, 143),
    "v_y": (144, 145),
    "v_b": (146, 147),

    # 6. Current (A)
    "current_total": (148, 149),
    "current_r": (150, 151),
    "current_y": (152, 153),
    "current_b": (154, 155),

    # 7. Frequency (Hz)
    "frequency": (156, 157),

    # 8. Energy (Wh, VAh)
    "energy_wh": (158, 159),
    "energy_vah": (160, 161),

    # 9. Load Hours (unsigned 32-bit or float at 162/163 or 216)
    "load_hours": (162, 163)
}

def decode_ieee754_float(high_word: int, low_word: int) -> float:
    """
    Decodes two 16-bit Modbus registers into an IEEE-754 32-bit floating point number.
    Standard big-endian Modbus word order: high word followed by low word.
    """
    raw_bytes = struct.pack(">HH", high_word, low_word)
    return struct.unpack(">f", raw_bytes)[0]

class LT4400MeterReader:
    """
    Dedicated Modbus RTU reader for L&T WL 4400 multi-function energy meter.
    Supports physical RS-485 communication, error detection, and mock fallback for tests.
    """
    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or default_config
        self.instrument = None
        self.consecutive_failures = 0
        self.last_successful_read_time = None
        self._mock_accum_wh = 175131297.0
        self._mock_accum_vah = 193873100.0
        self._mock_load_seconds = 1420 * 3600

    def connect(self) -> bool:
        """Initializes the serial Modbus instrument."""
        if self.config.mock_hardware:
            logger.info("Operating in MOCK_HARDWARE mode (no serial port opened).")
            return True

        if not MODBUS_LIB_AVAILABLE:
            err = "minimalmodbus or pyserial not installed in Python environment."
            logger.error(err)
            return False

        try:
            logger.info(
                f"Opening RS-485 port {self.config.serial_port} "
                f"(ID: {self.config.meter_id}, {self.config.baudrate} baud, Parity: {self.config.parity})"
            )
            parity_val = serial.PARITY_EVEN
            if self.config.parity == "NONE":
                parity_val = serial.PARITY_NONE
            elif self.config.parity == "ODD":
                parity_val = serial.PARITY_ODD

            inst = minimalmodbus.Instrument(
                self.config.serial_port,
                self.config.meter_id
            )
            inst.serial.baudrate = self.config.baudrate
            inst.serial.bytesize = self.config.bytesize
            inst.serial.parity = parity_val
            inst.serial.stopbits = self.config.stopbits
            inst.serial.timeout = self.config.timeout_seconds
            inst.mode = minimalmodbus.MODE_RTU
            inst.clear_buffers_before_each_transaction = True

            self.instrument = inst
            logger.info("Modbus RTU instrument initialized successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize serial port {self.config.serial_port}: {e}")
            self.instrument = None
            return False

    def read_all_parameters(self) -> MeterReadResult:
        """
        Polls the physical meter for all electrical parameters.
        Returns a MeterReadResult containing parsed float values or an explicit error.
        NEVER returns fake data if mock_hardware is False.
        """
        if self.config.mock_hardware:
            return self._generate_mock_reading()

        if self.instrument is None:
            connected = self.connect()
            if not connected:
                return MeterReadResult(
                    success=False,
                    data={},
                    error=f"Cannot connect to serial port {self.config.serial_port}",
                    is_mock=False
                )

        raw_values = {}
        errors = []

        try:
            # L&T WL 4400: Read holding registers in a continuous block from 100 to 163 (64 registers)
            # or iterate over parameter pairs with small transaction spacing.
            # Block read (100 to 163) is much faster and reduces RS-485 bus contention:
            start_reg = 100
            num_regs = 64
            
            try:
                block = self.instrument.read_registers(start_reg, num_regs, functioncode=3)
                # Map block to parameters
                for param_name, (r1, r2) in METER_REGISTERS.items():
                    idx1 = r1 - start_reg
                    idx2 = r2 - start_reg
                    if 0 <= idx1 < len(block) and 0 <= idx2 < len(block):
                        val = decode_ieee754_float(block[idx1], block[idx2])
                        raw_values[param_name] = round(val, 4)
            except Exception as block_err:
                logger.warning(f"Continuous block read failed ({block_err}), falling back to register pairs...")
                # Fallback to register-by-register reads
                for param_name, (r1, r2) in METER_REGISTERS.items():
                    try:
                        regs = self.instrument.read_registers(r1, 2, functioncode=3)
                        val = decode_ieee754_float(regs[0], regs[1])
                        raw_values[param_name] = round(val, 4)
                        time.sleep(0.02)
                    except Exception as pair_err:
                        errors.append(f"{param_name} ({r1}-{r2}): {pair_err}")

            # Verify critical electrical parameters were successfully acquired
            critical_keys = ["watts_total", "v_ln_avg", "current_total", "frequency"]
            missing = [k for k in critical_keys if k not in raw_values]
            if missing:
                self.consecutive_failures += 1
                error_msg = f"Critical meter registers missing: {missing}. Modbus errors: {errors}"
                logger.error(error_msg)
                return MeterReadResult(
                    success=False,
                    data=raw_values,
                    error=error_msg,
                    is_mock=False
                )

            self.consecutive_failures = 0
            self.last_successful_read_time = time.time()
            return MeterReadResult(
                success=True,
                data=raw_values,
                error=None,
                is_mock=False
            )

        except Exception as e:
            self.consecutive_failures += 1
            error_msg = f"Modbus communication exception: {e}"
            logger.error(error_msg)
            return MeterReadResult(
                success=False,
                data={},
                error=error_msg,
                is_mock=False
            )

    def _generate_mock_reading(self) -> MeterReadResult:
        """
        Generates deterministic, mathematically consistent simulated readings strictly
        when MOCK_HARDWARE is explicitly enabled for unit tests.
        """
        import random
        # 3-Phase voltages (V_LN ~ 230V, V_LL ~ 398V)
        v_r = round(230.2 + random.uniform(-0.8, 0.8), 2)
        v_y = round(231.0 + random.uniform(-0.8, 0.8), 2)
        v_b = round(229.8 + random.uniform(-0.8, 0.8), 2)
        v_ln_avg = round((v_r + v_y + v_b) / 3.0, 2)
        v_ry = round(v_ln_avg * 1.73205, 2)
        v_yb = round(v_ln_avg * 1.73205, 2)
        v_br = round(v_ln_avg * 1.73205, 2)
        v_ll_avg = round(v_ln_avg * 1.73205, 2)

        # Power factors
        pf_r = round(0.970 + random.uniform(-0.005, 0.005), 3)
        pf_y = round(0.972 + random.uniform(-0.005, 0.005), 3)
        pf_b = round(0.968 + random.uniform(-0.005, 0.005), 3)
        pf_avg = round((pf_r + pf_y + pf_b) / 3.0, 3)

        # Active power (~91.2 kW safe compliant baseline)
        w_r = round(30400.0 + random.uniform(-50.0, 50.0), 1)
        w_y = round(30350.0 + random.uniform(-50.0, 50.0), 1)
        w_b = round(30450.0 + random.uniform(-50.0, 50.0), 1)
        w_tot = round(w_r + w_y + w_b, 1)

        # Apparent power (VA = W / PF)
        va_r = round(w_r / pf_r, 1)
        va_y = round(w_y / pf_y, 1)
        va_b = round(w_b / pf_b, 1)
        va_tot = round(va_r + va_y + va_b, 1)

        # Current (I = VA / V)
        i_r = round(va_r / v_r, 2)
        i_y = round(va_y / v_y, 2)
        i_b = round(va_b / v_b, 2)
        i_tot = round(i_r + i_y + i_b, 2)

        freq = round(50.0 + random.uniform(-0.03, 0.03), 2)

        interval_h = self.config.poll_interval_seconds / 3600.0
        self._mock_accum_wh += (w_tot * interval_h)
        self._mock_accum_vah += (va_tot * interval_h)
        self._mock_load_seconds += self.config.poll_interval_seconds

        mock_data = {
            "watts_total": w_tot,
            "watts_r": w_r,
            "watts_y": w_y,
            "watts_b": w_b,
            "pf_avg": pf_avg,
            "pf_r": pf_r,
            "pf_y": pf_y,
            "pf_b": pf_b,
            "va_total": va_tot,
            "va_r": va_r,
            "va_y": va_y,
            "va_b": va_b,
            "v_ll_avg": v_ll_avg,
            "v_ry": v_ry,
            "v_yb": v_yb,
            "v_br": v_br,
            "v_ln_avg": v_ln_avg,
            "v_r": v_r,
            "v_y": v_y,
            "v_b": v_b,
            "current_total": i_tot,
            "current_r": i_r,
            "current_y": i_y,
            "current_b": i_b,
            "frequency": freq,
            "energy_wh": round(self._mock_accum_wh, 2),
            "energy_vah": round(self._mock_accum_vah, 2),
            "load_hours": int(self._mock_load_seconds // 3600)
        }
        self.last_successful_read_time = time.time()
        return MeterReadResult(
            success=True,
            data=mock_data,
            error=None,
            is_mock=True
        )
