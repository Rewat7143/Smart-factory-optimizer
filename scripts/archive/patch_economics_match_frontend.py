import re

file_path = 'backend/ml/economics.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """    def get_opportunities(self, factory_state: dict) -> list:
        return [
                {
                    'opportunity_id': 'OPP-001',
                    'category': 'PEAK_SHAVING',
                    'asset_id': 'HVAC-001',
                    'asset_name': 'Roof HVAC Unit',
                    'confidence': '92.5%',
                    'production_impact': 'None (Safe Zone)',
                    'recommended_action': 'Adjust temperature setpoint down by 1.5C at 05:00, allow float during 14:00-18:00.',
                    'status': 'PREDICTED',
                    'expected_kw_change': '-15.0 kW',
                    'potential_monthly_inr': '₹25,000',
                    'production_constraint': 'Temperature must remain below 24C to prevent condensation.',
                    'description': 'Pre-cool during off-peak to shave 15kW during peak hours.'
                },
                {
                    'opportunity_id': 'OPP-002',
                    'category': 'IDLE_REDUCTION',
                    'asset_id': 'CMP-001',
                    'asset_name': 'Auxiliary Compressor',
                    'confidence': '85.0%',
                    'production_impact': 'Negligible',
                    'recommended_action': 'Schedule automatic shutdown of Aux Compressor from 23:00 to 06:00.',
                    'status': 'ACTION_REQUIRED',
                    'expected_kw_change': '-12.5 kW',
                    'potential_monthly_inr': '₹20,000',
                    'production_constraint': 'Main line pressure must not drop below 80 PSI.',
                    'description': 'Pneumatic demand is near zero during 3rd shift.'
                }
            ]"""

pattern = r'\s*def get_opportunities\(self, factory_state: dict\) ->.*?(?=\n\s*def|\Z)'
content = re.sub(pattern, "\n" + replacement + "\n", content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
