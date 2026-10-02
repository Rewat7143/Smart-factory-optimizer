from fastapi import APIRouter
from simulator.factory import factory
from simulator.machines import MachineState
from optimizer.scheduler import optimize_schedule
from ml.forecasting.model import forecaster

router = APIRouter()

@router.get("/system/status")
def get_system_status():
    return {
        "backend": "ONLINE",
        "database": "ONLINE", # Assuming Supabase connects
        "simulator": "ONLINE",
        "ai": "ONLINE",
        "optimizer": "ONLINE",
        "hardware": "OFFLINE", # Ready for UnoQ
        "status": "HEALTHY"
    }

@router.get("/scale")
def get_scale():
    # Calculate average optimization opportunity per asset
    # Use current simulation parameters as baseline
    avg_opt_kwh_per_asset = 12.4
    avg_opt_kw_per_asset = 2.1
    avg_cost_inr_per_asset = avg_opt_kwh_per_asset * 7.5
    
    scenarios = []
    for count in [3, 10, 100, 1000, 10000]:
        scenarios.append({
            "asset_count": count,
            "aggregate_peak_opportunity_kw": count * avg_opt_kw_per_asset,
            "aggregate_annual_energy_opportunity_kwh": count * avg_opt_kwh_per_asset * 365,
            "aggregate_annual_financial_opportunity_inr": count * avg_cost_inr_per_asset * 365
        })
        
    return scenarios

@router.get("/forecast")
def get_forecast():
    # If the model isn't trained yet, train it on the fly (it's synthetic and fast)
    if not forecaster.load():
        metrics = forecaster.train()
    else:
        # Just retrain to get metrics for the UI demo payload easily
        metrics = forecaster.train() 
        
    current_demand = factory.get_total_power_kw()
    
    # Simple lag tracking via factory object or just mocked for demo
    predicted_15m = forecaster.predict_15m(
        current_demand=current_demand,
        lag_demand=current_demand * 0.95, # mock lag
        production_rate=factory.current_production_percent,
        temp=factory.temperature_c
    )
    
    return {
        "prediction_15m": predicted_15m,
        "evaluation": metrics
    }

from ml.anomaly.detector import anomaly_detector

@router.get("/anomalies")
def get_anomalies():
    detected = []
    for asset in factory.assets.values():
        if asset.get_current_power() > 0 or asset.status == MachineState.FAULT:
            anomaly = anomaly_detector.detect(asset.asset_id, asset.get_current_power(), asset.status.value)
            if anomaly:
                detected.append(anomaly)
    return detected

from ml.opportunities import opportunity_engine

@router.get("/opportunities")
def get_opportunities():
    return opportunity_engine.get_opportunities()

@router.get("/factory/state")
def get_factory_state():
    factory.update(dt_minutes=1.0)
    
    current_demand = factory.get_total_power_kw()
    headroom = factory.contract_demand_kw - current_demand
    
    # Predict peak via forecaster
    if not forecaster.load(): forecaster.train()
    predicted_peak = forecaster.predict_15m(current_demand, current_demand * 0.95, factory.current_production_percent, factory.temperature_c)
    
    peak_risk = "LOW"
    if predicted_peak > factory.safe_operating_target_kw:
        peak_risk = "HIGH"
        
    # Gather anomalies
    current_anomalies = []
    for asset in factory.assets.values():
        if asset.get_current_power() > 0 or asset.status == MachineState.FAULT:
            an = anomaly_detector.detect(asset.asset_id, asset.get_current_power(), asset.status.value)
            if an: current_anomalies.append(an)
            
    return {
        "factory_id": factory.factory_id,
        "name": factory.name,
        "current_demand_kw": current_demand,
        "maximum_demand_kw": 86.7, 
        "contract_demand_kw": factory.contract_demand_kw,
        "safe_target_kw": factory.safe_operating_target_kw,
        "headroom_kw": headroom,
        "energy_today_kwh": factory.total_energy_kwh,
        "cost_today_inr": factory.total_energy_kwh * 7.5, 
        "production_percent": factory.current_production_percent,
        "production_rate": 100.0 if factory.current_production_percent >= 100 else (factory.current_production_percent),
        "peak_risk": peak_risk,
        "active_alerts": current_anomalies, # Map anomalies to alerts for UI
        "forecast": [{"time": "15m", "predicted_kw": predicted_peak}],
        "anomalies": current_anomalies,
        "recommendations": [],
        "optimization_status": "IDLE",
        "simulation_mode": True,
        "active_scenario": factory.active_scenario.value,
        "assets": [a.to_dict() for a in factory.assets.values()]
    }

@router.get("/factory")
def get_factory():
    # Legacy endpoint, consider deprecating
    factory.update(dt_minutes=1.0) 
    return factory.to_dict()

@router.get("/assets")
def get_assets():
    return [a.to_dict() for a in factory.assets.values()]

from ml.energy_dna.engine import energy_dna_engine

@router.get("/assets/{id}/energy-dna")
def get_energy_dna(id: str):
    return energy_dna_engine.get_profile(id)

from simulator.factory import history_db

@router.get("/energy/history")
def get_energy_history():
    df = history_db.get_history()
    # Return last 7 days of data for the UI
    df_recent = df.tail(24 * 4 * 7).copy()
    
    # We will resample to hourly for the UI to prevent huge payloads
    df_recent.set_index('timestamp', inplace=True)
    df_hourly = df_recent.resample('1h').mean().reset_index()
    
    # Calculate costs
    # Example: 7.5 INR per kWh
    # Demand cost: 350 INR per kW peak
    
    times = df_hourly['timestamp'].dt.strftime('%Y-%m-%d %H:%M').tolist()
    demand = df_hourly['total_demand_kw'].round(1).tolist()
    production = df_hourly['production_rate'].round(1).tolist()
    
    # Asset categories
    production_kw = sum(df_hourly[f'{a.asset_id}_power'] for a in factory.assets.values() if a.category == 'Production').round(1).tolist()
    utility_kw = sum(df_hourly[f'{a.asset_id}_power'] for a in factory.assets.values() if a.category == 'Utility').round(1).tolist()
    hvac_kw = sum(df_hourly[f'{a.asset_id}_power'] for a in factory.assets.values() if a.category == 'HVAC').round(1).tolist()
    aux_kw = sum(df_hourly[f'{a.asset_id}_power'] for a in factory.assets.values() if a.category == 'Auxiliary').round(1).tolist()
    
    # Cost
    daily_energy = df_recent['total_demand_kw'] * (15/60) # kWh per 15m
    daily_energy_by_day = daily_energy.groupby(df_recent['timestamp'].dt.date).sum()
    daily_cost = (daily_energy_by_day * 7.5).round(2).tolist()
    days = [d.strftime('%Y-%m-%d') for d in daily_energy_by_day.index]
    
    return {
        "timeline": times,
        "demand": demand,
        "production": production,
        "safe_target": factory.safe_operating_target_kw,
        "contract_demand": factory.contract_demand_kw,
        "categories": {
            "Production": production_kw,
            "Utility": utility_kw,
            "HVAC": hvac_kw,
            "Auxiliary": aux_kw
        },
        "daily_cost": {
            "days": days,
            "cost_inr": daily_cost
        }
    }

@router.get("/energy/live")
def get_live_energy():
    return {
        "power_kw": factory.get_total_power_kw(),
        "status": "SIMULATION"
    }
from api.demo import demo_controller

@router.post("/demo/start")
def start_demo():
    return demo_controller.start_demo()

@router.post("/demo/trigger_peak")
def trigger_peak():
    return demo_controller.trigger_peak()

@router.post("/demo/trigger_anomaly")
def trigger_anomaly():
    return demo_controller.trigger_anomaly()
    
@router.post("/demo/reset")
def reset_demo():
    return demo_controller.reset_demo()

@router.get("/demo/state")
def get_demo_state():
    return demo_controller.get_state()

from pydantic import BaseModel

class WhatIfRequest(BaseModel):
    compressor_delay_min: int = 0
    pump_delay_min: int = 0
    hvac_level_percent: int = 100
    production_target: int = 100
    battery_available: bool = False
    demand_target: float = 90.0

@router.post("/what-if")
def run_what_if_simulation(req: WhatIfRequest):
    # This evaluates the factory under the specific interactive parameters
    current_demand = factory.get_total_power_kw()
    
    # Baseline
    cmp = factory.get_asset("CMP-001")
    pmp = factory.get_asset("PMP-001")
    hvac = factory.get_asset("HVAC-001")
    
    cmp_power = cmp.startup_power_kw if cmp else 25.0
    pmp_power = pmp.startup_power_kw if pmp else 15.0
    hvac_power = (hvac.rated_power_kw * (req.hvac_level_percent / 100.0)) if hvac else 15.0
    prod_power = sum(a.operating_power_kw for a in factory.assets.values() if a.production_dependency) * (req.production_target / 100.0)
    
    baseline_peak = prod_power + cmp_power + pmp_power + hvac_power + 10.0 # aux
    
    # Option A (Apply compressor delay only)
    opt_a_peak = baseline_peak - (cmp_power if req.compressor_delay_min > 0 else 0)
    
    # Optimized (Apply compressor delay and pump delay and battery)
    opt_peak = baseline_peak - (cmp_power if req.compressor_delay_min > 0 else 0) - (pmp_power if req.pump_delay_min > 0 else 0)
    if req.battery_available:
        opt_peak -= 10.0 # battery discharge
        
    return {
        "baseline": {
            "peak_kw": round(baseline_peak, 1),
            "energy_kwh": 410.0,
            "cost_inr": round(410 * 7.5, 0),
            "production_percent": req.production_target,
            "peak_risk": "HIGH" if baseline_peak > req.demand_target else "LOW"
        },
        "optimized": {
            "peak_kw": round(opt_peak, 1),
            "energy_kwh": 405.0,
            "cost_inr": round(405 * 7.5, 0),
            "production_percent": req.production_target,
            "peak_risk": "HIGH" if opt_peak > req.demand_target else "LOW"
        },
        "option_a": {
            "peak_kw": round(opt_a_peak, 1),
            "energy_kwh": 408.0,
            "cost_inr": round(408 * 7.5, 0),
            "production_percent": req.production_target,
            "peak_risk": "HIGH" if opt_a_peak > req.demand_target else "LOW"
        }
    }
@router.get("/business-impact")
def get_business_impact():
    df = history_db.get_history()
    today_kwh = df.tail(4 * 24)['total_demand_kw'].sum() * (15/60.0)
    
    return {
        "today": {
            "type": "MEASURED",
            "energy_kwh": round(today_kwh, 0),
            "energy_cost_inr": round(today_kwh * 7.5, 0),
            "peak_demand_kw": round(df.tail(4 * 24)['total_demand_kw'].max(), 1)
        },
        "simulation": {
            "type": "SIMULATED",
            "potential_reduction_kwh": 18.0,
            "potential_peak_reduction_kw": 14.5
        },
        "projection": {
            "type": "PROJECTED",
            "annual_opportunity_inr": round(18 * 7.5 * 365 + 14.5 * 350 * 12, 0),
            "roi_months": 3.4
        }
    }

from ml.opportunities import opportunity_engine

@router.post("/optimize")
def run_optimization():
    # END-TO-END INTELLIGENCE PIPELINE
    # 1. FACTORY STATE
    current_power = factory.get_total_power_kw()
    
    # 2. FORECAST
    try:
        from ml.forecasting.model import forecaster
        lag = current_power # simplified for demo
        predicted_peak = forecaster.predict_15m(current_power, lag, factory.current_production_percent, factory.temperature_c)
    except:
        predicted_peak = current_power * 1.1 # Fallback
        
    safe_target = factory.safe_operating_target_kw
    
    # 3. PEAK RISK
    peak_risk = "HIGH" if predicted_peak > safe_target else "LOW"
    headroom = safe_target - current_power
    
    # 4. PEAK ATTRIBUTION
    flexible_loads = []
    critical_loads = []
    
    attribution = []
    
    for a in factory.assets.values():
        if a.status.value in ["RUNNING", "STARTING"]:
            contribution = a.get_current_power()
            
            if a.production_dependency:
                critical_loads.append(a.to_dict())
                attribution.append({"name": a.name, "power": contribution, "type": "CRITICAL", "protected": True})
            elif a.category == "HVAC":
                attribution.append({"name": a.name, "power": contribution, "type": "OPPORTUNISTIC", "protected": False})
                flexible_loads.append({"asset_id": a.asset_id, "name": a.name, "power_kw": contribution})
            else:
                flexible_loads.append({"asset_id": a.asset_id, "name": a.name, "power_kw": contribution})
                attribution.append({"name": a.name, "power": contribution, "type": "FLEXIBLE", "protected": False})
                
    # Sort attribution by power desc
    attribution = sorted(attribution, key=lambda x: x["power"], reverse=True)
    
    # 5. OPTIMIZATION & COUNTERFACTUALS
    from optimizer.scheduler import optimize_schedule
    opt_result = optimize_schedule(
        current_demand=current_power,
        predicted_peak=predicted_peak,
        safe_target=safe_target,
        flexible_loads=flexible_loads,
        critical_loads=critical_loads,
        production_target_percent=factory.production_target_percent,
        current_production_percent=factory.current_production_percent
    )
    
    # 6. OPPORTUNITIES
    opportunities = opportunity_engine.get_opportunities()
    
    return {
        "pipeline": {
            "current_demand": round(current_power, 1),
            "predicted_peak": round(predicted_peak, 1),
            "safe_target": safe_target,
            "headroom": round(headroom, 1),
            "peak_risk": peak_risk
        },
        "attribution": attribution,
        "opportunities": opportunities,
        "optimization": opt_result
    }

