from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from simulator.machines import MachineState

class DataSource(str, Enum):
    SIMULATOR = "SIMULATOR"
    UNO_Q = "UNO_Q"
    METER = "METER"
    RASPBERRY_PI = "RASPBERRY_PI"
    SIMULATED_RASPI = "SIMULATED_RASPI"
    PLC = "PLC"
    HISTORICAL_TEST = "HISTORICAL_TEST"

class DataQuality(str, Enum):
    GOOD = "GOOD"
    WARNING = "WARNING"
    BAD = "BAD"

class EnergyReading(BaseModel):
    timestamp: datetime
    factory_id: str
    asset_id: str
    
    # Standard aggregated fields (maintained for backward compatibility)
    voltage_v: Optional[float] = None
    current_a: Optional[float] = None
    active_power_kw: float
    apparent_power_kva: Optional[float] = None
    reactive_power_kvar: Optional[float] = None
    energy_kwh: float
    frequency_hz: Optional[float] = None
    power_factor: Optional[float] = None
    
    # Full 27 L&T WL4400 Modbus Memory Map parameters (40101 to 40217)
    # 1. Active Power (W)
    watts_total: Optional[float] = None   # 40101: Watts Total
    watts_r: Optional[float] = None       # 40103: Watts R phase
    watts_y: Optional[float] = None       # 40105: Watts Y phase
    watts_b: Optional[float] = None       # 40107: Watts B phase
    
    # 2. Power Factor
    pf_avg: Optional[float] = None        # 40117: PF Avg (inst)
    pf_r: Optional[float] = None          # 40119: PF R phase
    pf_y: Optional[float] = None          # 40121: PF Y phase
    pf_b: Optional[float] = None          # 40123: PF B phase
    
    # 3. Apparent Power (VA)
    va_total: Optional[float] = None      # 40125: VA total
    va_r: Optional[float] = None          # 40127: VA R phase
    va_y: Optional[float] = None          # 40129: VA Y phase
    va_b: Optional[float] = None          # 40131: VA B phase
    
    # 4. Line-to-Line Voltage (V)
    v_ll_avg: Optional[float] = None      # 40133: VL L average
    v_ry: Optional[float] = None          # 40135: VR Y phase
    v_yb: Optional[float] = None          # 40137: VY B phase
    v_br: Optional[float] = None          # 40139: VB R phase
    
    # 5. Line-to-Neutral Phase Voltage (V)
    v_ln_avg: Optional[float] = None      # 40141: VL N average
    v_r: Optional[float] = None           # 40143: V R phase
    v_y: Optional[float] = None           # 40145: V Y phase
    v_b: Optional[float] = None           # 40147: V B phase
    
    # 6. Current (A)
    current_total: Optional[float] = None # 40149: Current Total
    current_r: Optional[float] = None     # 40151: Current R phase
    current_y: Optional[float] = None     # 40153: Current Y phase
    current_b: Optional[float] = None     # 40155: Current B phase
    
    # 7. Frequency (Hz)
    frequency: Optional[float] = None     # 40157: Frequency
    
    # 8. Energy (Wh, VAh) & Load Hours
    energy_wh: Optional[float] = None     # 40159: Wh
    energy_vah: Optional[float] = None    # 40161: VAh
    load_hours: Optional[int] = None      # 40217: Load Hours (unsigned long)
    
    demand_kw: Optional[float] = None
    machine_state: MachineState = MachineState.RUNNING
    production_rate: Optional[float] = None
    production_target_percent: Optional[float] = None
    temperature_c: Optional[float] = None
    tariff_period: Optional[str] = None
    data_source: DataSource = DataSource.SIMULATOR
    data_quality: DataQuality = DataQuality.GOOD
