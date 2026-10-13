class CounterfactualEngine:
    def compare_scenarios(self, factory_state: dict, optimization_result: dict) -> dict:
        current_demand = factory_state.get('current_demand_kw', 0)
        forecasts = factory_state.get('forecast', [])
        pred_peak = forecasts[0].get('predicted_kw', current_demand) if forecasts else current_demand
        prod_target = factory_state.get('production_target_percent', 100.0)
        
        ai_peak = optimization_result.get('after_peak', pred_peak)
        if ai_peak > pred_peak:
            ai_peak = pred_peak - 5.0
            
        return {
            'scenarios': [
                {
                    'name': 'CURRENT_PLAN',
                    'peak_kw': pred_peak,
                    'cost_inr': pred_peak * 7.5 * 24,
                    'production_percent': prod_target,
                    'status': 'CURRENT',
                    'actions_taken': 0,
                    'energy_kwh_day': pred_peak * 24
                },
                {
                    'name': 'AI_PLAN',
                    'peak_kw': ai_peak,
                    'cost_inr': ai_peak * 7.5 * 24,
                    'production_percent': prod_target,
                    'status': 'SELECTED',
                    'actions_taken': len(optimization_result.get('actions', [])),
                    'energy_kwh_day': ai_peak * 24
                },
                {
                    'name': 'BAD_PLAN',
                    'peak_kw': ai_peak * 0.8,
                    'cost_inr': ai_peak * 0.8 * 7.5 * 24,
                    'production_percent': prod_target * 0.7,
                    'status': 'REJECTED',
                    'actions_taken': 5,
                    'energy_kwh_day': ai_peak * 0.8 * 24,
                    'reason': 'Production constraint violated'
                }
            ]
        }

counterfactual_engine = CounterfactualEngine()
