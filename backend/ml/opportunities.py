from datetime import datetime, timezone
from simulator.factory import factory, history_db
from ml.anomaly.detector import anomaly_detector

class OpportunityEngine:
    def get_opportunities(self):
        opportunities = []
        now_str = datetime.now(timezone.utc).isoformat()
        
        # 1. Check for overlapping startup (if current peak risk is high)
        total_power = factory.get_total_power_kw()
        starting_assets = [a for a in factory.assets.values() if a.status.value == "STARTING" and not a.production_dependency]
        
        if total_power > factory.safe_operating_target_kw and len(starting_assets) > 1:
            opportunities.append({
                "opportunity_id": f"OPP-{int(datetime.now().timestamp())}",
                "asset_id": starting_assets[0].asset_id,
                "asset_name": starting_assets[0].name,
                "category": "STARTUP_OVERLAP",
                "detected_at": now_str,
                "energy_opportunity_kwh": 0.0,
                "cost_opportunity_inr": 350.0, # Avoided peak penalty
                "production_impact": "NONE",
                "recommended_action": f"Delay {starting_assets[0].name} startup by 7 minutes to avoid overlap with {starting_assets[1].name}.",
                "confidence": "HIGH",
                "status": "ACTION_REQUIRED"
            })
            
        # 2. Check for Idle Waste using anomalies
        for asset in factory.assets.values():
            if asset.status.value == "IDLE":
                # Check anomaly
                an = anomaly_detector.detect(asset.asset_id, asset.get_current_power(), asset.status.value)
                if an and an.get("type") == "IDLE_WASTE":
                    opportunities.append({
                        "opportunity_id": f"OPP-IDLE-{asset.asset_id}",
                        "asset_id": asset.asset_id,
                        "asset_name": asset.name,
                        "category": "IDLE_WASTE",
                        "detected_at": now_str,
                        "energy_opportunity_kwh": round(asset.get_current_power() * 1.0, 1), # 1 hr approx
                        "cost_opportunity_inr": round(asset.get_current_power() * 7.5, 2),
                        "production_impact": "NONE",
                        "recommended_action": f"Switch {asset.name} from IDLE to OFF during non-production cycles.",
                        "confidence": "HIGH",
                        "status": "ACTION_REQUIRED"
                    })
                    
        # 3. HVAC Optimization (if temperature is low but HVAC power is high)
        hvac = factory.get_asset("HVAC-001")
        if hvac and hvac.get_current_power() > hvac.rated_power_kw * 0.7 and factory.temperature_c < 24.0:
            opportunities.append({
                "opportunity_id": "OPP-HVAC-SETPOINT",
                "asset_id": hvac.asset_id,
                "asset_name": hvac.name,
                "category": "HVAC_OPTIMIZATION",
                "detected_at": now_str,
                "energy_opportunity_kwh": round(hvac.get_current_power() * 0.15 * 8, 1), # 15% save over 8h
                "cost_opportunity_inr": round(hvac.get_current_power() * 0.15 * 8 * 7.5, 2),
                "production_impact": "NONE",
                "recommended_action": "Increase AC setpoint by 1.5°C; ambient temperature allows for lower duty cycle.",
                "confidence": "MEDIUM",
                "status": "NORMAL"
            })
            
        return opportunities

opportunity_engine = OpportunityEngine()
