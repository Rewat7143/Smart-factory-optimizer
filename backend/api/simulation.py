import time
import threading
from simulator.factory import factory
from simulator.machines import MachineState

class SimulationController:
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.tick_rate_seconds = 1.0 # 1 real second = 1 simulation minute
        
    def start(self):
        if not self.is_running:
            self.is_running = True
            # Set initial steady state if everything is OFF
            if factory.get_total_power_kw() < 10.0:
                factory.start_demo_production()
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            
    def stop(self):
        self.is_running = False
        
    def _run_loop(self):
        while self.is_running:
            try:
                # 1.0 dt_minutes advance
                factory.update(1.0)
            except Exception as e:
                print(f"Simulation tick error: {e}")
            time.sleep(self.tick_rate_seconds)

    def apply_control(self, control_params: dict):
        # Interpret control parameters
        if "compressor" in control_params:
            state = MachineState.RUNNING if control_params["compressor"] == "ON" else MachineState.OFF
            cmp = factory.get_asset("CMP-001")
            if cmp and cmp.status != state:
                cmp.update_state(state, 0.0)
                
        if "pump" in control_params:
            state = MachineState.RUNNING if control_params["pump"] == "ON" else MachineState.OFF
            pmp = factory.get_asset("PMP-001")
            if pmp and pmp.status != state:
                pmp.update_state(state, 0.0)
                
        if "production" in control_params:
            state = MachineState.RUNNING if control_params["production"] == "ON" else MachineState.OFF
            for a in factory.assets.values():
                if a.production_dependency and a.status != state:
                    a.update_state(state, 0.0)
                    
        if "fault" in control_params:
            # Trigger an anomaly
            m1 = factory.get_asset("M-001")
            if m1:
                m1.status = MachineState.FAULT
                
        return {"status": "SUCCESS"}

simulation_controller = SimulationController()
