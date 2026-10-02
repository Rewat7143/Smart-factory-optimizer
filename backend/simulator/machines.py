from enum import Enum
from typing import Optional, Dict

class MachineState(str, Enum):
    OFF = "OFF"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    STOPPING = "STOPPING"
    FAULT = "FAULT"
    MAINTENANCE = "MAINTENANCE"

class Criticality(str, Enum):
    CRITICAL = "CRITICAL"
    FLEXIBLE = "FLEXIBLE"
    OPPORTUNISTIC = "OPPORTUNISTIC"

class Asset:
    def __init__(self, asset_id: str, name: str, category: str, criticality: Criticality,
                 rated_power_kw: float, operating_power_kw: float, startup_power_kw: float,
                 idle_power_kw: float, startup_duration_minutes: float,
                 production_dependency: bool = False, minimum_runtime_minutes: float = 15,
                 minimum_off_time_minutes: float = 15):
        self.asset_id = asset_id
        self.name = name
        self.category = category
        self.criticality = criticality
        self.rated_power_kw = rated_power_kw
        self.operating_power_kw = operating_power_kw
        self.startup_power_kw = startup_power_kw
        self.idle_power_kw = idle_power_kw
        self.startup_duration_minutes = startup_duration_minutes
        self.production_dependency = production_dependency
        self.minimum_runtime_minutes = minimum_runtime_minutes
        self.minimum_off_time_minutes = minimum_off_time_minutes
        
        self.status = MachineState.OFF
        self.time_in_state = 0.0 # minutes
        
    def get_current_power(self) -> float:
        if self.status == MachineState.OFF:
            return 0.0
        elif self.status == MachineState.STARTING:
            return self.startup_power_kw
        elif self.status == MachineState.RUNNING:
            return self.operating_power_kw
        elif self.status == MachineState.IDLE:
            return self.idle_power_kw
        elif self.status == MachineState.STOPPING:
            return self.idle_power_kw / 2.0
        elif self.status == MachineState.FAULT:
            return self.rated_power_kw * 1.1 # abnormal power
        elif self.status == MachineState.MAINTENANCE:
            return 0.0
        return 0.0

    def update_state(self, new_state: MachineState, dt_minutes: float):
        if self.status != new_state:
            self.status = new_state
            self.time_in_state = 0.0
        else:
            self.time_in_state += dt_minutes
            
        # Handle automatic transitions
        if self.status == MachineState.STARTING and self.time_in_state >= self.startup_duration_minutes:
            self.status = MachineState.RUNNING
            self.time_in_state = 0.0

    def to_dict(self) -> Dict:
        return {
            "asset_id": self.asset_id,
            "name": self.name,
            "category": self.category,
            "status": self.status.value,
            "criticality": self.criticality.value,
            "power_kw": self.get_current_power(),
            "production_dependency": self.production_dependency
        }
