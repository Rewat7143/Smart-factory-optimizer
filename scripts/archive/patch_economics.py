import re

file_path = 'backend/ml/economics.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """    def get_opportunities(self, factory_state: dict) -> dict:
        return [
                {
                    'id': 'OPP-001',
                    'title': 'Shift HVAC Load',
                    'asset_id': 'HVAC-001',
                    'category': 'PEAK_SHAVING',
                    'potential_monthly_inr': 25000,
                    'potential_monthly_kwh': 3000,
                    'confidence_percent': 92.5,
                    'description': 'Pre-cool during off-peak to shave 15kW during peak hours.',
                    'action': 'Adjust temperature setpoint down by 1.5C at 05:00, allow float during 14:00-18:00',
                    'expected_kw_change': -15.0,
                    'production_constraint': 'Temperature must remain below 24C to prevent condensation.',
                    'status': 'PREDICTED'
                },
                {
                    'id': 'OPP-002',
                    'title': 'Compressor Idle Reduction',
                    'asset_id': 'CMP-001',
                    'category': 'IDLE_REDUCTION',
                    'potential_monthly_inr': 20000,
                    'potential_monthly_kwh': 2500,
                    'confidence_percent': 85.0,
                    'description': 'Pneumatic demand is near zero during 3rd shift. Power down auxiliary compressor.',
                    'action': 'Schedule automatic shutdown of Aux Compressor from 23:00 to 06:00',
                    'expected_kw_change': -12.5,
                    'production_constraint': 'Main line pressure must not drop below 80 PSI.',
                    'status': 'PREDICTED'
                }
            ]"""

pattern = r'\s*def get_opportunities\(self, factory_state: dict\) -> dict:.*?\]\s*\}'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
