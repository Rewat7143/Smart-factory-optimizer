from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timezone

client = TestClient(app)

def test_telemetry_ingestion():
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "RASPBERRY_PI",
        "device_id": "RPi-TEST-01",
        "voltage": 230.5,
        "current": 2.1,
        "active_power_kw": 0.483,
        "energy_kwh": 100.5,
        "frequency_hz": 50.0,
        "power_factor": 0.95
    }
    
    # Ingest
    response = client.post("/api/telemetry/ingest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] is True
    assert data["source"] == "RASPBERRY_PI"
    assert data["device_id"] == "RPi-TEST-01"
    
    # Check Health
    health_res = client.get("/api/telemetry/health")
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert len(health_data) >= 1
    device_health = next(d for d in health_data if d["device_id"] == "RPi-TEST-01")
    assert device_health["status"] == "CONNECTED"
    
    # Check Latest
    latest_res = client.get("/api/telemetry/latest")
    assert latest_res.status_code == 200
    latest_data = latest_res.json()
    assert latest_data["status"] == "CONNECTED"
    assert latest_data["reading"]["asset_id"] == "RPi-TEST-01"
    assert latest_data["reading"]["active_power_kw"] == 0.483

def test_27_parameters_memory_map_ingestion():
    """Verify ingestion of all 27 parameters from the L&T WL4400 memory map (addresses 40101-40217)."""
    payload_27 = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "SIMULATED_RASPI",
        "device_id": "RPi-METER-01",
        # 40101-40107 Active Power (float)
        "watts_total": 16120.0,
        "watts_r": 5410.0,
        "watts_y": 5230.0,
        "watts_b": 5480.0,
        # 40117-40123 Power Factor (float)
        "pf_avg": 0.950,
        "pf_r": 0.948,
        "pf_y": 0.957,
        "pf_b": 0.945,
        # 40125-40131 Apparent Power (float)
        "va_total": 16968.4,
        "va_r": 5706.7,
        "va_y": 5465.0,
        "va_b": 5798.9,
        # 40133-40139 Line Voltage (float)
        "v_ll_avg": 399.2,
        "v_ry": 398.8,
        "v_yb": 399.7,
        "v_br": 399.1,
        # 40141-40147 Phase Voltage (float)
        "v_ln_avg": 230.5,
        "v_r": 230.2,
        "v_y": 231.1,
        "v_b": 230.2,
        # 40149-40155 Current (float)
        "current_total": 73.61,
        "current_r": 24.79,
        "current_y": 23.65,
        "current_b": 25.19,
        # 40157 Frequency (float)
        "frequency": 50.02,
        # 40159 Wh (float)
        "energy_wh": 14210.5,
        # 40161 VAh (float)
        "energy_vah": 14958.4,
        # 40217 Load Hours (Unsigned long)
        "load_hours": 1420
    }

    res = client.post("/api/telemetry/ingest", json=payload_27)
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["accepted"] is True
    assert res_data["persistence"]["database"] == "PERSISTED"

    # Check latest reading has all 27 attributes
    latest_res = client.get("/api/telemetry/latest")
    assert latest_res.status_code == 200
    r = latest_res.json()["reading"]
    assert r["watts_total"] == 16120.0
    assert r["watts_r"] == 5410.0
    assert r["watts_y"] == 5230.0
    assert r["watts_b"] == 5480.0
    assert r["pf_avg"] == 0.950
    assert r["pf_r"] == 0.948
    assert r["pf_y"] == 0.957
    assert r["pf_b"] == 0.945
    assert r["va_total"] == 16968.4
    assert r["v_ll_avg"] == 399.2
    assert r["v_ln_avg"] == 230.5
    assert r["current_total"] == 73.61
    assert r["frequency"] == 50.02
    assert r["energy_wh"] == 14210.5
    assert r["energy_vah"] == 14958.4
    assert r["load_hours"] == 1420
    # Backward compatibility checks
    assert abs(r["active_power_kw"] - 16.12) < 0.01
    assert abs(r["energy_kwh"] - 14.2105) < 0.01

    # Check live dashboard has detailed 3-phase output
    dash_res = client.get("/api/live/dashboard")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["status"] == "ONLINE"
    assert "phases" in dash_data
    assert "R" in dash_data["phases"]
    assert "Y" in dash_data["phases"]
    assert "B" in dash_data["phases"]
    assert "unbalance" in dash_data["phases"]


def test_layman_analytics():
    """Verify layman analytics endpoint for field engineer dashboard."""
    res = client.get("/api/telemetry/layman_analytics")
    assert res.status_code == 200
    data = res.json()
    
    # Check contract demand
    cd = data["contract_demand"]
    assert cd["contract_limit_kw"] == 100.0
    assert cd["safe_target_kw"] == 90.0
    assert "peak_demand_kw" in cd
    assert "current_demand_kw" in cd
    assert "remaining_buffer_kw" in cd
    assert cd["status"] in ["SAFE", "CAUTION", "PENALTY_RISK"]
    
    # Check concentric radial rings (R, Y, B)
    rings = data["radial_rings"]
    assert len(rings) == 3
    assert rings[0]["name"] == "Phase R (Inner Ring)"
    assert rings[1]["name"] == "Phase Y (Middle Ring)"
    assert rings[2]["name"] == "Phase B (Outer Ring)"
    
    # Check time horizons (day, week, month, year)
    tf = data["timeframes"]
    assert "day" in tf and len(tf["day"]["labels"]) == 24
    assert "week" in tf and len(tf["week"]["labels"]) == 7
    assert "month" in tf and len(tf["month"]["labels"]) == 4
    assert "year" in tf and len(tf["year"]["labels"]) == 12
    
    # Check AI explanation
    ai = data["ai_explanation"]
    assert "title" in ai
    assert "summary" in ai
    assert len(ai["cards"]) == 4

    # Check Section B: Energy Consumption
    ec = data["energy_consumption"]
    assert "units_today" in ec
    assert "units_this_month" in ec
    assert "total_energy_kwh" in ec
    assert "total_apparent_energy_kvah" in ec

    # Check Section C: Maximum Demand (CMD)
    md = data["maximum_demand"]
    assert "current_demand_kw" in md
    assert "today_highest_peak_kw" in md
    assert "month_highest_peak_kw" in md
    assert md["configured_demand_limit_kw"] == 100.0
    assert "predicted_peak_kw" in md
    assert "predicted_peak_time" in md

    # Check Section D: Power Quality
    pq = data["power_quality"]
    assert "current_power_factor" in pq
    assert "today_power_factor" in pq
    assert "monthly_power_factor" in pq
    assert "voltage" in pq and "v_ln_avg" in pq["voltage"]
    assert "current" in pq and "current_total" in pq["current"]
    assert "frequency" in pq

    # Check Actual vs Forecast demand chart data
    af = data["actual_vs_forecast"]
    assert "hours" in af
    assert "actual_kw" in af
    assert af["cmd_limit_kw"] == 100.0
    assert "predicted_peak_kw" in af
    assert af["predicted_peak_kw"] >= 0.0
    assert "predicted_peak_time" in af

    # Check Industrial statements dictionary
    assert "pcc_monitoring" in data["industrial_statements"]
    assert "energy_consumption" in data["industrial_statements"]
    assert "maximum_demand" in data["industrial_statements"]
    assert "power_quality" in data["industrial_statements"]
    assert "operator_approval_required" in data["industrial_statements"]


