class EnergyEconomicsEngine:
    def get_kpi(self, factory_state: dict) -> dict:
        demand = factory_state.get('current_demand_kw', 100)
        prod_pct = factory_state.get('production_percent', 100)
        
        units = 170 * (prod_pct / 100.0)
        kwh = demand * 24 
        epu = kwh / (units * 24) if units > 0 else 0
        
        return {
            'energy_per_unit': round(epu, 2),
            'units_produced_today': round(units * 24, 0),
            'energy_consumed_kwh': round(kwh, 2),
            'yesterday_kpi': round(epu * 1.05, 2),
            'improvement_percent': 5.0,
            'iso50001_target': round(epu * 0.9, 2)
        }
    def get_opportunities(self, factory_state: dict) -> list:
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
            ]


economics_engine = EnergyEconomicsEngine()
