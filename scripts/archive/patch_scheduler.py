import re

def patch():
    with open('backend/optimizer/scheduler.py', 'r') as f:
        content = f.read()

    # We need to add the 'why' field to the 'actions' dict inside the optimization response.
    # Look for best_actions.append
    
    replacement = """
        best_actions.append({
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
"""
    
    content = re.sub(
        r'best_actions\.append\(\{.*?"reduction_kw": largest\[\'power_kw\'\]\s*\}\)',
        replacement,
        content,
        flags=re.DOTALL
    )
    
    with open('backend/optimizer/scheduler.py', 'w') as f:
        f.write(content)

patch()
