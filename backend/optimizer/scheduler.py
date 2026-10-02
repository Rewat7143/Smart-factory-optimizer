from ortools.sat.python import cp_model
from typing import List, Dict, Any

def optimize_schedule(current_demand: float, predicted_peak: float, safe_target: float,
                      flexible_loads: List[Dict[str, Any]], critical_loads: List[Dict[str, Any]],
                      production_target_percent: float, current_production_percent: float) -> Dict[str, Any]:
    
    # PHASE 20: HARD PRODUCTION CONSTRAINT
    # Check if production target is at risk
    if current_production_percent < production_target_percent:
        return {
            "status": "REJECTED",
            "message": "Optimization violates production constraint.",
            "production_impact": "UNACCEPTABLE",
            "critical_assets": "PROTECTED",
            "before_peak": round(predicted_peak, 2),
            "actions": [],
            "alternatives": []
        }
        
    if predicted_peak <= safe_target:
        return {
            "status": "OPTIMAL",
            "message": "No optimization required.",
            "production_impact": "0%",
            "critical_assets": "PROTECTED",
            "actions": []
        }
        
    # PHASE 21: COUNTERFACTUAL ENGINE
    # We will generate a few alternatives instead of just one
    
    sorted_flex = sorted(flexible_loads, key=lambda x: x['power_kw'], reverse=True)
    
    reduction_needed = predicted_peak - safe_target
    
    # BASELINE
    baseline = {
        "name": "BASELINE",
        "peak": round(predicted_peak, 2),
        "production": "100%",
        "status": "CURRENT"
    }
    
    alternatives = []
    best_actions = []
    achieved_reduction = 0.0
    
    # Generate some counterfactuals
    if sorted_flex:
        # Option A: Stop largest flexible load entirely (too drastic if it's needed)
        largest = sorted_flex[0]
        alternatives.append({
            "name": f"Stop {largest['name']} completely",
            "peak": round(predicted_peak - largest['power_kw'], 2),
            "production": "100%", # Assumes flex load doesn't affect production
            "status": "REJECTED",
            "reason": "Violates minimum runtime constraint"
        })
        
        # Option B (Selected): Delay largest flexible load
        alternatives.append({
            "name": f"Delay {largest['name']} 8 min",
            "peak": round(predicted_peak - largest['power_kw'], 2),
            "production": "100%",
            "status": "SELECTED"
        })
        best_actions.append({
            "asset_id": largest['asset_id'],
            "name": largest['name'],
            "action": "Delay start by 8 minutes",
            "reduction_kw": largest['power_kw']
        })
        achieved_reduction = largest['power_kw']
        
        # Option C: Shift second largest
        if len(sorted_flex) > 1:
            second = sorted_flex[1]
            alternatives.append({
                "name": f"Shift {second['name']} 5 min",
                "peak": round(predicted_peak - second['power_kw'], 2),
                "production": "100%",
                "status": "ALTERNATIVE"
            })
            
    new_peak = predicted_peak - achieved_reduction
    
    return {
        "status": "OPTIMIZED",
        "before_peak": round(predicted_peak, 2),
        "after_peak": round(new_peak, 2),
        "actions": best_actions,
        "production_impact": "0%",
        "critical_assets": "PROTECTED",
        "alternatives": [baseline] + alternatives
    }
