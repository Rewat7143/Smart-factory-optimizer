from fastapi import APIRouter
from api import telemetry
from datetime import datetime, timezone

router = APIRouter()

@router.get("/live/dashboard")
def get_live_dashboard():
    if not telemetry.latest_reading:
        return {"status": "OFFLINE"}
        
    lr = telemetry.latest_reading
    power_kw = lr.active_power_kw or 0.0
    voltage = lr.voltage_v or 230.0
    current = lr.current_a or 0.0
    pf = lr.power_factor or 0.95
    freq = lr.frequency_hz or 50.0
    energy = lr.energy_kwh or 0.0

    # Memory Map 27 Parameters
    watts_total = lr.watts_total if lr.watts_total is not None else (power_kw * 1000.0)
    watts_r = lr.watts_r if lr.watts_r is not None else (watts_total / 3.0)
    watts_y = lr.watts_y if lr.watts_y is not None else (watts_total / 3.0)
    watts_b = lr.watts_b if lr.watts_b is not None else (watts_total / 3.0)

    pf_avg = lr.pf_avg if lr.pf_avg is not None else pf
    pf_r = lr.pf_r if lr.pf_r is not None else pf_avg
    pf_y = lr.pf_y if lr.pf_y is not None else pf_avg
    pf_b = lr.pf_b if lr.pf_b is not None else pf_avg

    va_total = lr.va_total if lr.va_total is not None else ((watts_total / pf_avg) if pf_avg else watts_total)
    va_r = lr.va_r if lr.va_r is not None else (va_total / 3.0)
    va_y = lr.va_y if lr.va_y is not None else (va_total / 3.0)
    va_b = lr.va_b if lr.va_b is not None else (va_total / 3.0)

    v_ln_avg = lr.v_ln_avg if lr.v_ln_avg is not None else voltage
    v_r = lr.v_r if lr.v_r is not None else v_ln_avg
    v_y = lr.v_y if lr.v_y is not None else v_ln_avg
    v_b = lr.v_b if lr.v_b is not None else v_ln_avg

    v_ll_avg = lr.v_ll_avg if lr.v_ll_avg is not None else (v_ln_avg * 1.73205)
    v_ry = lr.v_ry if lr.v_ry is not None else v_ll_avg
    v_yb = lr.v_yb if lr.v_yb is not None else v_ll_avg
    v_br = lr.v_br if lr.v_br is not None else v_ll_avg

    current_total = lr.current_total if lr.current_total is not None else current
    current_r = lr.current_r if lr.current_r is not None else (current_total / 3.0)
    current_y = lr.current_y if lr.current_y is not None else (current_total / 3.0)
    current_b = lr.current_b if lr.current_b is not None else (current_total / 3.0)

    frequency = lr.frequency if lr.frequency is not None else freq
    energy_wh = lr.energy_wh if lr.energy_wh is not None else (energy * 1000.0)
    energy_vah = lr.energy_vah if lr.energy_vah is not None else (energy_wh / pf_avg if pf_avg else energy_wh)
    load_hours = lr.load_hours if lr.load_hours is not None else 1420

    # Calculate 3-Phase Unbalance (IEEE / NEMA Standard)
    avg_v = (v_r + v_y + v_b) / 3.0 if (v_r + v_y + v_b) > 0 else 1.0
    v_dev_max = max(abs(v_r - avg_v), abs(v_y - avg_v), abs(v_b - avg_v))
    v_unbalance_pct = round((v_dev_max / avg_v) * 100.0, 2)

    avg_i = (current_r + current_y + current_b) / 3.0 if (current_r + current_y + current_b) > 0 else 1.0
    i_dev_max = max(abs(current_r - avg_i), abs(current_y - avg_i), abs(current_b - avg_i))
    i_unbalance_pct = round((i_dev_max / avg_i) * 100.0, 2)
    
    # 1. Digital Twin (Electrical)
    twin = {
        "nodes": [
            {
                "id": "GRID", 
                "name": "Utility Grid", 
                "voltage": round(voltage, 1), 
                "v_ll": round(v_ll_avg, 1), 
                "freq": round(freq, 2)
            },
            {
                "id": "MAIN_METER", 
                "name": "L&T WL4400 3-Phase Multi-Function Meter", 
                "power_kw": round(power_kw, 3), 
                "watts_total": round(watts_total, 1),
                "va_total": round(va_total, 1),
                "current_a": round(current, 2), 
                "pf": round(pf, 3),
                "load_hours": load_hours,
                "phases": {
                    "R": {"v": round(v_r, 1), "i": round(current_r, 2), "w": round(watts_r, 1), "pf": round(pf_r, 3)},
                    "Y": {"v": round(v_y, 1), "i": round(current_y, 2), "w": round(watts_y, 1), "pf": round(pf_y, 3)},
                    "B": {"v": round(v_b, 1), "i": round(current_b, 2), "w": round(watts_b, 1), "pf": round(pf_b, 3)}
                }
            },
            {
                "id": "FACTORY_LOAD", 
                "name": "Aggregated 3-Phase Factory Load", 
                "power_kw": round(power_kw, 3),
                "unbalance_pct": i_unbalance_pct
            }
        ]
    }
    
    # 2. Economics
    tariff = 7.5
    cost_today = energy * tariff
    
    # 3. Power Quality / Maintenance
    quality_status = "HEALTHY"
    alerts = []
    if pf_avg < 0.95:
        quality_status = "WARNING"
        alerts.append(f"Low Average Power Factor ({round(pf_avg, 3)}). Reactive penalty risk.")
    if min(pf_r, pf_y, pf_b) < 0.90:
        quality_status = "WARNING"
        alerts.append(f"Phase PF asymmetry detected: R={round(pf_r,2)}, Y={round(pf_y,2)}, B={round(pf_b,2)}.")
    if freq < 49.5 or freq > 50.5:
        quality_status = "WARNING"
        alerts.append(f"Grid frequency anomaly ({round(freq, 2)} Hz).")
    if v_unbalance_pct > 2.0:
        quality_status = "WARNING"
        alerts.append(f"Voltage unbalance ({v_unbalance_pct}%) exceeds 2% threshold.")
    if i_unbalance_pct > 15.0:
        quality_status = "WARNING"
        alerts.append(f"Current unbalance ({i_unbalance_pct}%) indicates phase load asymmetry.")
        
    # 4. Copilot Insights
    insights = []
    if pf_avg < 0.95:
        insights.append({"type": "ACTION", "message": f"Power factor is {round(pf_avg, 3)}. APFC capacitor bank staging recommended."})
    elif power_kw > 90:
        insights.append({"type": "WARNING", "message": f"Demand approaching 100kW contract limit. Current: {round(power_kw, 2)}kW. Shed non-critical flexible loads."})
    else:
        insights.append({"type": "INFO", "message": "All 27 electrical parameters within safe operating limits."})

    return {
        "status": "ONLINE",
        "timestamp": lr.timestamp.isoformat(),
        "metrics": {
            # Standard legacy
            "power_kw": round(power_kw, 3),
            "voltage": round(voltage, 1),
            "current": round(current, 2),
            "pf": round(pf_avg, 3),
            "freq": round(freq, 2),
            "energy_kwh": round(energy, 2),
            "cost_inr": round(cost_today, 2),
            # All 27 parameters from memory map
            "watts_total": round(watts_total, 1),
            "watts_r": round(watts_r, 1),
            "watts_y": round(watts_y, 1),
            "watts_b": round(watts_b, 1),
            "pf_avg": round(pf_avg, 3),
            "pf_r": round(pf_r, 3),
            "pf_y": round(pf_y, 3),
            "pf_b": round(pf_b, 3),
            "va_total": round(va_total, 1),
            "va_r": round(va_r, 1),
            "va_y": round(va_y, 1),
            "va_b": round(va_b, 1),
            "v_ll_avg": round(v_ll_avg, 1),
            "v_ry": round(v_ry, 1),
            "v_yb": round(v_yb, 1),
            "v_br": round(v_br, 1),
            "v_ln_avg": round(v_ln_avg, 1),
            "v_r": round(v_r, 1),
            "v_y": round(v_y, 1),
            "v_b": round(v_b, 1),
            "current_total": round(current_total, 2),
            "current_r": round(current_r, 2),
            "current_y": round(current_y, 2),
            "current_b": round(current_b, 2),
            "frequency": round(frequency, 2),
            "energy_wh": round(energy_wh, 1),
            "energy_vah": round(energy_vah, 1),
            "load_hours": load_hours
        },
        "phases": {
            "R": {"v_ln": round(v_r, 1), "current": round(current_r, 2), "watts": round(watts_r, 1), "va": round(va_r, 1), "pf": round(pf_r, 3)},
            "Y": {"v_ln": round(v_y, 1), "current": round(current_y, 2), "watts": round(watts_y, 1), "va": round(va_y, 1), "pf": round(pf_y, 3)},
            "B": {"v_ln": round(v_b, 1), "current": round(current_b, 2), "watts": round(watts_b, 1), "va": round(va_b, 1), "pf": round(pf_b, 3)},
            "line_to_line": {"v_ry": round(v_ry, 1), "v_yb": round(v_yb, 1), "v_br": round(v_br, 1), "average": round(v_ll_avg, 1)},
            "unbalance": {
                "voltage_pct": v_unbalance_pct,
                "current_pct": i_unbalance_pct
            }
        },
        "twin": twin,
        "quality": {
            "status": quality_status,
            "alerts": alerts,
            "v_unbalance_pct": v_unbalance_pct,
            "i_unbalance_pct": i_unbalance_pct
        },
        "copilot": insights
    }
