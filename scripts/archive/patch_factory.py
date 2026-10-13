import re

file_path = 'backend/simulator/factory.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
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
"""

# Replace __init__
pattern = r'\s*def __init__\(self.*?\n        self\._initialize_assets\(\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

replacement2 = """
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
"""

pattern2 = r'\s*def update\(self, dt_minutes: float\):.*?\s*def _apply_scenario_behaviors\(self\):'
content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
