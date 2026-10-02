from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class FactoryState(BaseModel):
    factory_id: str
    name: str
    
    current_demand_kw: float
    maximum_demand_kw: float
    contract_demand_kw: float
    safe_target_kw: float
    headroom_kw: float
    
    energy_today_kwh: float
    cost_today_inr: float
    
    production_percent: float
    production_rate: float
    
    peak_risk: str # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    
    active_alerts: List[Dict[str, Any]]
    forecast: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    
    optimization_status: str
    simulation_mode: bool
    active_scenario: str
    
    assets: List[Dict[str, Any]]
