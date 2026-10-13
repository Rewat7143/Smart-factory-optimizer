import re

file_path = 'backend/ml/maintenance.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
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
"""

pattern = r'\s*def evaluate_health\(self, factory_state: dict\):.*?return sorted\(results, key=lambda x: x\[\'health_score\'\]\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
