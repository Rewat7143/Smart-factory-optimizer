import re

file_path = 'backend/simulator/factory.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
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
"""

pattern = r'\s*def set_scenario.*?a\.status = MachineState\.RUNNING'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
