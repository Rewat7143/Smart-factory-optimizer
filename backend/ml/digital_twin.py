import datetime

class DigitalTwinEngine:
    def get_twin_state(self, factory_state: dict) -> dict:
        assets = factory_state.get('assets', [])
        current_demand_kw = factory_state.get('current_demand_kw', 0.0)
        contract_demand_kw = factory_state.get('contract_demand_kw', 100.0)
        safe_target_kw = factory_state.get('safe_target_kw', 90.0)
        
        nodes = []
        power_balance = {
            'production_kw': 0.0, 'utility_kw': 0.0, 'hvac_kw': 0.0, 'auxiliary_kw': 0.0, 'storage_kw': 0.0
        }
        
        for a in assets:
            kw = a.get('operating_power_kw', 0.0)
            rated = a.get('rated_power_kw', 1.0) or 1.0
            load_pct = (kw / rated) * 100.0
            nodes.append({
                'asset_id': a.get('asset_id'),
                'name': a.get('name'),
                'category': a.get('category'),
                'power_kw': kw,
                'rated_power_kw': rated,
                'load_percent': round(load_pct, 2),
                'status': a.get('status'),
                'criticality': a.get('criticality'),
                'production_dependency': a.get('production_dependency'),
                'power_flow_direction': 'consuming' if kw > 0 else 'idle'
            })
            
            cat = str(a.get('category', '')).upper()
            if 'HVAC' in cat: power_balance['hvac_kw'] += kw
            elif 'PUMP' in cat or 'COMPRESSOR' in cat or 'AUX' in cat: power_balance['auxiliary_kw'] += kw
            elif 'BATTERY' in cat or 'STORAGE' in cat: power_balance['storage_kw'] += kw
            elif a.get('production_dependency'): power_balance['production_kw'] += kw
            else: power_balance['utility_kw'] += kw
        
        forecast = factory_state.get('forecast', [])
        trend = 0
        if forecast and len(forecast) > 0:
            pred = forecast[0].get('predicted_kw', current_demand_kw)
            trend = (pred - current_demand_kw) / 15.0 # per minute trend based on 15m forecast
        
        return {
            'topology': nodes,
            'aggregate_metrics': {
                'total_load_kw': current_demand_kw,
                'contract_demand_kw': contract_demand_kw,
                'safe_target_kw': safe_target_kw,
                'headroom_kw': safe_target_kw - current_demand_kw,
                'load_factor_percent': round((current_demand_kw / contract_demand_kw) * 100, 2) if contract_demand_kw else 0
            },
            'predicted_state': {
                '+5min': current_demand_kw + trend * 5,
                '+10min': current_demand_kw + trend * 10,
                '+15min': current_demand_kw + trend * 15,
            },
            'risk_assessment': {
                'current_risk': 'HIGH' if current_demand_kw > safe_target_kw else 'LOW',
                'predicted_risk': 'HIGH' if (current_demand_kw + trend * 15) > safe_target_kw else 'LOW',
                'time_to_breach_minutes': max(0, (safe_target_kw - current_demand_kw) / trend) if trend > 0 and current_demand_kw < safe_target_kw else 0
            },
            'power_balance': power_balance
        }

digital_twin = DigitalTwinEngine()
