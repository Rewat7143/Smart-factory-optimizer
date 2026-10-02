from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from simulator.machines import MachineState

class DataSource(str, Enum):
    SIMULATOR = "SIMULATOR"
    UNO_Q = "UNO_Q"
    METER = "METER"
    PLC = "PLC"

class DataQuality(str, Enum):
    GOOD = "GOOD"
    WARNING = "WARNING"
    BAD = "BAD"

class EnergyReading(BaseModel):
    timestamp: datetime
    factory_id: str
    asset_id: str
    
    voltage_v: Optional[float] = None
    current_a: Optional[float] = None
    
    active_power_kw: float
    apparent_power_kva: Optional[float] = None
    reactive_power_kvar: Optional[float] = None
    
    energy_kwh: float
    
    frequency_hz: Optional[float] = None
    power_factor: Optional[float] = None
    
    demand_kw: Optional[float] = None
    
    machine_state: MachineState
    
    production_rate: Optional[float] = None
    production_target_percent: Optional[float] = None
    temperature_c: Optional[float] = None
    
    tariff_period: Optional[str] = None
    
    data_source: DataSource = DataSource.SIMULATOR
    data_quality: DataQuality = DataQuality.GOOD
