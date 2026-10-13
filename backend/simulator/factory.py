from typing import List, Dict, Optional
from datetime import datetime, timezone
import random

from simulator.machines import Asset, MachineState, Criticality
from simulator.scenarios import FactoryScenario
from schemas.energy import EnergyReading, DataSource, DataQuality

class FactoryModel:
    def __init__(self, name: str = "Demo Manufacturing Plant", contract_demand_kw: float = 100.0,
                 safe_operating_target_kw: float = 90.0, demand_interval_min: int = 15):
        self.factory_id = "fac_001"
        self.name = name
        self.contract_demand_kw = contract_demand_kw
        self.safe_operating_target_kw = safe_operating_target_kw
        self.demand_interval_min = demand_interval_min
        
        self.production_target_percent = 100.0
        self.current_production_percent = 0.0
        self.temperature_c = 25.0
        self.active_scenario = FactoryScenario.NORMAL_PRODUCTION
        self.total_energy_kwh = 0.0
        self.sim_time_minutes = 0.0
        
        self.assets: Dict[str, Asset] = {}
        self._initialize_assets()

        
    def _initialize_assets(self):
        # Critical Production Motors
        self.add_asset(Asset("M-001", "Production Motor 01", "Production", Criticality.CRITICAL, 
                             rated_power_kw=15.0, operating_power_kw=14.0, startup_power_kw=25.0, idle_power_kw=2.0, startup_duration_minutes=1.0, production_dependency=True))
        self.add_asset(Asset("M-002", "Production Motor 02", "Production", Criticality.CRITICAL, 
                             rated_power_kw=18.0, operating_power_kw=16.5, startup_power_kw=30.0, idle_power_kw=2.5, startup_duration_minutes=1.5, production_dependency=True))
        self.add_asset(Asset("M-003", "Production Motor 03", "Production", Criticality.CRITICAL, 
                             rated_power_kw=10.0, operating_power_kw=9.5, startup_power_kw=18.0, idle_power_kw=1.5, startup_duration_minutes=0.5, production_dependency=True))
                             
        # Flexible Utility
        self.add_asset(Asset("CMP-001", "Air Compressor", "Utility", Criticality.FLEXIBLE, 
                             rated_power_kw=30.0, operating_power_kw=28.5, startup_power_kw=38.0, idle_power_kw=4.0, startup_duration_minutes=2.0, production_dependency=False))
        self.add_asset(Asset("PMP-001", "Process Pump", "Utility", Criticality.FLEXIBLE, 
                             rated_power_kw=25.0, operating_power_kw=22.5, startup_power_kw=30.0, idle_power_kw=3.0, startup_duration_minutes=1.0, production_dependency=False))
                             
        # Opportunistic HVAC
        self.add_asset(Asset("HVAC-001", "HVAC System", "HVAC", Criticality.OPPORTUNISTIC, 
                             rated_power_kw=20.0, operating_power_kw=15.0, startup_power_kw=22.0, idle_power_kw=5.0, startup_duration_minutes=3.0, production_dependency=False))
                             
        # Others
        self.add_asset(Asset("BAT-001", "Battery / Energy Storage", "Storage", Criticality.FLEXIBLE, 
                             rated_power_kw=10.0, operating_power_kw=-10.0, startup_power_kw=0.0, idle_power_kw=0.0, startup_duration_minutes=0.0, production_dependency=False))
        self.add_asset(Asset("AUX-001", "Auxiliary Load", "Auxiliary", Criticality.FLEXIBLE, 
                             rated_power_kw=5.0, operating_power_kw=4.0, startup_power_kw=5.0, idle_power_kw=1.0, startup_duration_minutes=0.0, production_dependency=False))

    def add_asset(self, asset: Asset):
        self.assets[asset.asset_id] = asset

    def get_asset(self, asset_id: str) -> Asset:
        return self.assets.get(asset_id)

    def get_total_power_kw(self) -> float:
        return sum(asset.get_current_power() for asset in self.assets.values())
    def update(self, dt_minutes: float):
        self.sim_time_minutes = (self.sim_time_minutes + dt_minutes) % 60.0
        self._cycle_phases()
        
        # Apply scenario behaviors
        self._apply_scenario_behaviors()

        # Update asset states
        for asset in self.assets.values():
            asset.update_state(asset.status, dt_minutes)
            
        # Update factory-level properties
        running_critical = sum(1 for a in self.assets.values() if a.production_dependency and a.status == MachineState.RUNNING)
        total_critical = sum(1 for a in self.assets.values() if a.production_dependency)
        
        self.current_production_percent = (running_critical / total_critical) * 100.0 if total_critical > 0 else 0.0
        # Accumulate energy
        power = self.get_total_power_kw()
        self.total_energy_kwh += power * (dt_minutes / 60.0)
        # Push to history
        global history_db
        from datetime import datetime, timezone
        if 'history_db' in globals() and history_db.history_df is not None:
            history_db.append_reading(datetime.now(timezone.utc), power, self.current_production_percent)



    def _cycle_phases(self):
        t = self.sim_time_minutes
        if 0 <= t < 15:
            self.set_scenario(FactoryScenario.NORMAL_PRODUCTION)
        elif 15 <= t < 25:
            self.set_scenario(FactoryScenario.HIGH_PRODUCTION)
        elif 25 <= t < 35:
            # Sudden startup of a high-load machine (e.g. big pump)
            pmp = self.get_asset("PMP-001")
            if pmp and pmp.status == MachineState.OFF: 
                pmp.update_state(MachineState.STARTING, 0.0)
            self.set_scenario(FactoryScenario.NORMAL_PRODUCTION)
        elif 35 <= t < 40:
            self.set_scenario(FactoryScenario.PEAK_RISK)
        elif 40 <= t < 45:
            self.set_scenario(FactoryScenario.MACHINE_ANOMALY)
        elif 45 <= t < 50:
            self.set_scenario(FactoryScenario.IDLE_WASTE)
        else:
            self.set_scenario(FactoryScenario.NORMAL_PRODUCTION)

    def _apply_scenario_behaviors(self):

        if self.active_scenario == FactoryScenario.PEAK_RISK:
            # Compressor and Pump overlap
            cmp = self.get_asset("CMP-001")
            pmp = self.get_asset("PMP-001")
            if cmp and cmp.status == MachineState.OFF: cmp.update_state(MachineState.STARTING, 0.0)
            if pmp and pmp.status == MachineState.OFF: pmp.update_state(MachineState.STARTING, 0.0)
            
        elif self.active_scenario == FactoryScenario.MACHINE_ANOMALY:
            # Compressor gets stuck at higher power
            cmp = self.get_asset("CMP-001")
            if cmp: cmp.status = MachineState.FAULT
            
        elif self.active_scenario == FactoryScenario.IDLE_WASTE:
            # Critical motors left idle instead of off
            for a in self.assets.values():
                if a.production_dependency and a.status == MachineState.OFF:
                    a.status = MachineState.IDLE
                    
        elif self.active_scenario == FactoryScenario.HIGH_PRODUCTION:
            self.temperature_c = 28.0 # increases HVAC
            hvac = self.get_asset("HVAC-001")
            if hvac and hvac.status == MachineState.OFF:
                hvac.update_state(MachineState.RUNNING, 0.0)
    def set_scenario(self, scenario: FactoryScenario):
        self.active_scenario = scenario
        if scenario == FactoryScenario.NORMAL_PRODUCTION:
            # Restore normal states
            for a in self.assets.values():
                if a.status == MachineState.FAULT or a.status == MachineState.IDLE:
                    a.update_state(MachineState.RUNNING, 0)
            
            # Turn off utility overlapping loads that were started during peak
            cmp = self.get_asset("CMP-001")
            pmp = self.get_asset("PMP-001")
            if cmp: cmp.update_state(MachineState.OFF, 0)
            if pmp: pmp.update_state(MachineState.OFF, 0)


    def start_demo_production(self):
        self.active_scenario = FactoryScenario.NORMAL_PRODUCTION
        for asset in self.assets.values():
            if asset.asset_id != "BAT-001":
                asset.update_state(MachineState.STARTING, 0.0)

    def get_energy_readings(self) -> List[EnergyReading]:
        now = datetime.now(timezone.utc)
        readings = []
        for asset in self.assets.values():
            kw = asset.get_current_power()
            reading = EnergyReading(
                timestamp=now,
                factory_id=self.factory_id,
                asset_id=asset.asset_id,
                active_power_kw=kw,
                energy_kwh=kw * (1.0/60.0), # Assuming 1 min interval for instantaneous reading
                machine_state=asset.status,
                production_rate=self.current_production_percent if asset.production_dependency else None,
                production_target_percent=self.production_target_percent,
                temperature_c=self.temperature_c,
                data_source=DataSource.SIMULATOR,
                data_quality=DataQuality.GOOD
            )
            readings.append(reading)
        return readings

    def to_dict(self) -> Dict:
        return {
            "factory_id": self.factory_id,
            "name": self.name,
            "contract_demand_kw": self.contract_demand_kw,
            "safe_operating_target_kw": self.safe_operating_target_kw,
            "current_demand_kw": self.get_total_power_kw(),
            "production_target_percent": self.production_target_percent,
            "current_production_percent": self.current_production_percent,
            "active_scenario": self.active_scenario.value,
            "total_energy_kwh": self.total_energy_kwh,
            "temperature_c": self.temperature_c,
            "assets": [a.to_dict() for a in self.assets.values()]
        }

# Global instance for the simulator backend
factory = FactoryModel()

from simulator.history import HistoryGenerator
history_db = HistoryGenerator(factory)
history_db.generate() # Generate on startup

