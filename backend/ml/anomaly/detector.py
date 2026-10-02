import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime, timezone
from simulator.factory import history_db

class AnomalyDetector:
    def __init__(self):
        self.models = {}
        self.baseline_stats = {}
        
    def train_baseline(self, asset_id: str):
        df = history_db.get_history()
        col = f'{asset_id}_power'
        if col not in df.columns:
            return
            
        asset_power = df[col].values.reshape(-1, 1)
        
        # Train IsolationForest for this specific asset
        model = IsolationForest(contamination=0.01, random_state=42)
        model.fit(asset_power)
        self.models[asset_id] = model
        
        self.baseline_stats[asset_id] = {
            'mean': np.mean(asset_power),
            'std': np.std(asset_power),
            'min': np.min(asset_power),
            'max': np.max(asset_power)
        }
        
    def detect(self, asset_id: str, current_power: float, asset_state: str):
        if asset_id not in self.models:
            self.train_baseline(asset_id)
            
        if asset_id not in self.models: return None
        
        model = self.models[asset_id]
        baseline = self.baseline_stats[asset_id]
        
        # Predict anomaly
        pred = model.predict([[current_power]])[0]
        
        expected_range = f"{round(baseline['min'], 1)} - {round(baseline['max'], 1)} kW"
        
        # Force anomaly if FAULT, otherwise use model
        if pred == -1 or asset_state == "FAULT":
            deviation = 0
            if baseline['mean'] > 0:
                deviation = ((current_power - baseline['mean']) / baseline['mean']) * 100
                
            severity = "WARNING" if abs(deviation) < 20 else "CRITICAL"
            
            anomaly_type = "UNEXPECTED_POWER"
            if asset_state == "IDLE" and deviation > 0:
                anomaly_type = "IDLE_WASTE"
                
            return {
                "asset_id": asset_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": anomaly_type,
                "observed_power": round(current_power, 2),
                "expected_range": expected_range,
                "deviation_percent": round(deviation, 1),
                "severity": severity,
                "estimated_cost_impact": round(abs(current_power - baseline['mean']) * 7.5 * 24, 2)
            }
        
        return None

# Global instance
anomaly_detector = AnomalyDetector()
