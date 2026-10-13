from ortools.sat.python import cp_model
from typing import List, Dict, Any

def optimize_schedule(current_demand: float, predicted_peak: float, safe_target: float,
                      flexible_loads: List[Dict[str, Any]], critical_loads: List[Dict[str, Any]],
                      production_target_percent: float, current_production_percent: float) -> Dict[str, Any]:
    
    if current_production_percent < production_target_percent:
        return {
            "status": "REJECTED",
            "message": "It violates production constraint.",
            "production_impact": "UNACCEPTABLE",
            "critical_assets": "PROTECTED",
            "actions": [], "alternatives": [{"name": "BASELINE", "peak": round(predicted_peak, 2), "production": f"{current_production_percent}%", "status": "CURRENT"}],
            "alternatives": []
        }

    # 1. No optimization needed if safe
    if predicted_peak <= safe_target:
        return {
            "status": "OPTIMAL",
            "message": "Plant operating within safe contract limits. Baseline schedule is optimal.",
            "production_impact": "0%",
            "critical_assets": "PROTECTED",
            "before_peak": round(predicted_peak, 2),
            "after_peak": round(predicted_peak, 2),
            "actions": [],
            "alternatives": [{"name": "BASELINE", "peak": round(predicted_peak, 2), "production": f"{current_production_percent}%", "status": "CURRENT"}]
        }
        
    # 2. Optimization Required - Generate Counterfactuals
    sorted_flex = sorted(flexible_loads, key=lambda x: x['power_kw'], reverse=True)
    reduction_needed = predicted_peak - safe_target
    
    baseline = {
        "name": "BASELINE",
        "peak": round(predicted_peak, 2),
        "production": f"{current_production_percent}%",
        "status": "CURRENT"
    }
    
    alternatives = []
    best_actions = []
    achieved_reduction = 0.0
    
    # OPTION A: Attempt to stop a critical production load (Must be rejected)
    if critical_loads:
        crit = critical_loads[0]
        alternatives.append({
            "name": f"Stop {crit.get('name', crit.get('asset_id'))}",
            "peak": round(predicted_peak - crit['power_kw'], 2),
            "production": "0%", # Drops production
            "status": "REJECTED",
            "reason": "Violates production constraint"
        })
        
    # OPTION B: Shift flexible load
    if sorted_flex:
        largest = sorted_flex[0]
        alternatives.append({
            "name": f"Delay {largest.get('name', largest.get('asset_id'))} 8 min",
            "peak": round(predicted_peak - largest['power_kw'], 2),
            "production": f"{current_production_percent}%",
            "status": "SELECTED"
        })
        
        best_actions.append({
            "asset": largest['asset_id'],
            "asset_id": largest['asset_id'],
            "name": largest.get('name', largest.get('asset_id')),
            "action": f"Delay {largest.get('name', largest.get('asset_id'))} startup by 8 minutes",
            "reduction_kw": largest['power_kw'],
            "why": {
                "peak_risk": "HIGH",
                "reasons": [
                    f"Production already consuming {round(current_production_percent,1)}% capacity",
                    f"{largest.get('name', largest.get('asset_id'))} startup adds {largest['power_kw']} kW",
                    f"Demand forecast exceeds safe threshold by {round(reduction_needed, 1)} kW"
                ],
                "protected": "Production Line Assets",
                "flexible": largest.get('name', largest.get('asset_id'))
            }
        })

        achieved_reduction = largest['power_kw']
        
    new_peak = predicted_peak - achieved_reduction
    
    # If we STILL couldn't find a solution, then we truly reject
    if not best_actions:
         return {
            "status": "REJECTED",
            "message": "No flexible loads available to reduce peak without violating production constraint.",
            "production_impact": "UNACCEPTABLE",
            "critical_assets": "PROTECTED",
            "before_peak": round(predicted_peak, 2),
            "actions": [], "alternatives": [{"name": "BASELINE", "peak": round(predicted_peak, 2), "production": f"{current_production_percent}%", "status": "CURRENT"}],
            "alternatives": [baseline] + alternatives
        }
    
    return {
        "status": "OPTIMIZED",
        "before_peak": round(predicted_peak, 2),
        "after_peak": round(new_peak, 2),
        "actions": best_actions,
        "production_impact": "0%",
        "critical_assets": "PROTECTED",
        "alternatives": [baseline] + alternatives
    }
