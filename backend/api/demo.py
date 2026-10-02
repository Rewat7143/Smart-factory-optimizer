import time
import threading
from simulator.factory import factory, FactoryScenario

class DemoController:
    def __init__(self):
        self.state = "NORMAL"
        self.scenario_thread = None
        
    def get_state(self):
        return {"demo_state": self.state}
        
    def reset_demo(self):
        self.state = "NORMAL"
        factory.set_scenario(FactoryScenario.NORMAL)
        return self.get_state()
        
    def trigger_peak(self):
        self.state = "PEAK_RISK"
        factory.set_scenario(FactoryScenario.PEAK_RISK)
        return self.get_state()
        
    def trigger_anomaly(self):
        self.state = "ANOMALY"
        factory.set_scenario(FactoryScenario.MACHINE_ANOMALY)
        return self.get_state()
        
    def _run_sequence(self):
        self.reset_demo()
        time.sleep(30) # 0:30 Production reaches 100%
        
        # 1:00 Compressor Starts
        time.sleep(30)
        
        # 1:20 Pump Starts (Simulated by Peak Risk Scenario)
        time.sleep(20)
        self.trigger_peak()
        
        # 2:00 AI detects etc. handled by frontend polling the state
        
        # 3:15 Anomaly
        time.sleep(75)
        self.trigger_anomaly()
        
        # 3:45 Reset
        time.sleep(30)
        self.reset_demo()

    def start_demo(self):
        if self.scenario_thread is None or not self.scenario_thread.is_alive():
            self.scenario_thread = threading.Thread(target=self._run_sequence)
            self.scenario_thread.start()
            self.state = "RUNNING_SEQUENCE"
        return self.get_state()

demo_controller = DemoController()
