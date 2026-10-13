import re

file_path = 'backend/ml/opportunities.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
    def get_opportunities(self, mode: str = "SIMULATION"):
        from api.routes import _get_factory_state
        state = _get_factory_state(mode)
        
        opportunities = []
        now_str = datetime.now(timezone.utc).isoformat()
        
        total_power = state.get("current_demand_kw", 0.0)
        safe_target = state.get("contract_demand_kw", 100.0)
        assets = state.get("assets", [])
        
        # 1. Check for overlapping startup
        starting_assets = [a for a in assets if a.get("status") == "STARTING" and not a.get("production_dependency", True)]
        
        if total_power > safe_target and len(starting_assets) > 1:
            opportunities.append({
                "opportunity_id": f"OPP-{int(datetime.now().timestamp())}",
                "asset_id": starting_assets[0].get("asset_id"),
                "asset_name": starting_assets[0].get("name"),
                "category": "STARTUP_OVERLAP",
                "detected_at": now_str,
                "energy_opportunity_kwh": 0.0,
                "cost_opportunity_inr": 350.0, # Avoided peak penalty
                "expected_reduction_kw": starting_assets[0].get("power_kw", 0),
                "production_impact": "NONE",
                "recommended_action": f"Delay {starting_assets[0].get('name')} startup by 7 minutes to avoid overlap.",
                "confidence": "HIGH",
                "status": "ACTION_REQUIRED"
            })
            
        # 2. Check for Idle Waste using anomalies
        for asset in assets:
            if asset.get("status") == "IDLE" and asset.get("power_kw", 0) is not None:
                an = anomaly_detector.detect(asset.get("asset_id"), asset.get("power_kw", 0), "IDLE")
                if an and an.get("type") == "IDLE_WASTE":
                    opportunities.append({
                        "opportunity_id": f"OPP-IDLE-{asset.get('asset_id')}",
                        "asset_id": asset.get("asset_id"),
                        "asset_name": asset.get("name"),
                        "category": "IDLE_WASTE",
                        "detected_at": now_str,
                        "energy_opportunity_kwh": round(asset.get("power_kw", 0) * 1.0, 1),
                        "cost_opportunity_inr": round(asset.get("power_kw", 0) * 7.5, 2),
                        "expected_reduction_kw": asset.get("power_kw", 0),
                        "production_impact": "NONE",
                        "recommended_action": f"Switch {asset.get('name')} from IDLE to OFF during non-production cycles.",
                        "confidence": "HIGH",
                        "status": "ACTION_REQUIRED"
                    })
                    
        return opportunities
"""

pattern = r'\s*def get_opportunities\(self\):.*?return opportunities'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
