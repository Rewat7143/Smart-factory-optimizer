from typing import Dict, Any
from simulator.factory import factory, history_db
import pandas as pd

class EnergyDNAEngine:
    def get_profile(self, asset_id: str) -> Dict[str, Any]:
        df = history_db.get_history()
        col = f'{asset_id}_power'
        
        asset = factory.get_asset(asset_id)
        if not asset or col not in df.columns:
            return {}
            
        power_series = df[col]
        active_power = power_series[power_series > asset.idle_power_kw + 0.1]
        
        avg_op = active_power.mean() if not active_power.empty else 0
        med_op = active_power.median() if not active_power.empty else 0
        peak = power_series.max()
        idle = power_series[power_series <= asset.idle_power_kw + 0.1].mean()
        
        # Calculate daily energy
        daily_kwh = power_series.sum() * (15 / 60.0) / history_db.days
        
        return {
            "asset_id": asset.asset_id,
            "name": asset.name,
            "average_operating_power_kw": round(avg_op, 1),
            "median_operating_power_kw": round(med_op, 1),
            "peak_power_kw": round(peak, 1),
            "idle_power_kw": round(idle, 1) if pd.notna(idle) else 0,
            "startup_power_kw": asset.startup_power_kw,
            "startup_duration_minutes": asset.startup_duration_minutes,
            "daily_energy_kwh": round(daily_kwh, 1),
            "peak_contribution_percent": round((avg_op / factory.contract_demand_kw) * 100, 1),
            "baseline_power_kw": round(avg_op, 1),
            "energy_variability": "HIGH" if active_power.std() > 5 else "LOW",
            "efficiency_trend": "STABLE",
            "normal_operating_range": f"{round(active_power.quantile(0.05), 1) if not active_power.empty else 0} - {round(active_power.quantile(0.95), 1) if not active_power.empty else 0} kW"
        }

energy_dna_engine = EnergyDNAEngine()
