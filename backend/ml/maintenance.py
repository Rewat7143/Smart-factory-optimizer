import numpy as np
from datetime import datetime, timezone
import random

class PredictiveMaintenanceEngine:
    def __init__(self):
        self.asset_health = {}
    def evaluate_health(self, factory_state: dict):
        results = []
        from ml.anomaly.detector import anomaly_detector
        
        has_submetering = factory_state.get('submetering_available', False)
        
        for asset in factory_state.get('assets', []):
            asset_id = asset['asset_id']
            power = asset.get('power_kw')
            
            if not has_submetering or power is None:
                results.append({
                    "asset_id": asset_id,
                    "name": asset.get('name', asset_id),
                    "health_score": None,
                    "vibration_mms": None,
                    "estimated_ttf_days": None,
                    "status": "UNMONITORED",
                    "recommendation": "Submetering or vibration sensors required for ML inference."
                })
                continue
                
            # Check for actual anomalies instead of random numbers
            an = anomaly_detector.detect(asset_id, power, asset.get('status', 'RUNNING'))
            
            if an and an.get('severity') == 'CRITICAL':
                results.append({
                    "asset_id": asset_id,
                    "name": asset.get('name', asset_id),
                    "health_score": 30.0, # proxy for critical anomaly
                    "vibration_mms": None,
                    "estimated_ttf_days": 0,
                    "status": "CRITICAL",
                    "recommendation": "Unexpected power signature detected. Inspect immediately."
                })
            elif an and an.get('severity') == 'WARNING':
                results.append({
                    "asset_id": asset_id,
                    "name": asset.get('name', asset_id),
                    "health_score": 60.0,
                    "vibration_mms": None,
                    "estimated_ttf_days": None,
                    "status": "WARNING",
                    "recommendation": "Minor power deviation detected. Monitor operations."
                })
            else:
                results.append({
                    "asset_id": asset_id,
                    "name": asset.get('name', asset_id),
                    "health_score": 95.0,
                    "vibration_mms": None,
                    "estimated_ttf_days": None,
                    "status": "HEALTHY",
                    "recommendation": "No anomalies detected in power signature."
                })
                
        return results

        
    def _get_recommendation(self, status, asset_id):
        if status == "CRITICAL":
            return "Schedule immediate maintenance. Bearing wear pattern detected."
        elif status == "WARNING":
            return "Monitor vibration closely. Plan lubrication in next 48h."
        return "Operating optimally. Continue normal operations."

maintenance_engine = PredictiveMaintenanceEngine()
