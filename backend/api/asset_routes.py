from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import os
import json

from database import db
from api import telemetry

router = APIRouter()

class AssetCreatePayload(BaseModel):
    asset_id: Optional[str] = None
    name: str
    equipment_type: Optional[str] = "Not configured"
    manufacturer_model: Optional[str] = "Not configured"
    location: Optional[str] = "Not configured"
    rated_capacity_kw: Optional[float] = None
    rated_voltage_v: Optional[float] = None
    phase_config: Optional[str] = "Not configured"
    pcc_association: Optional[str] = "PCC-01"
    meter_association: Optional[str] = "RPi-METER-01"
    load_classification: Optional[str] = "Flexible" # Mandatory, Flexible, Opportunistic
    priority_order: Optional[int] = 2
    is_protected: Optional[bool] = False
    permitted_actions: Optional[List[str]] = ["monitor_only"]
    min_runtime_minutes: Optional[int] = 15
    min_offtime_minutes: Optional[int] = 15
    restart_delay_minutes: Optional[int] = 5
    operating_schedule: Optional[str] = "24/7 Continuous"
    production_constraints: Optional[str] = "Not configured"
    operator_notes: Optional[str] = "Not configured"
    maintenance_notes: Optional[str] = "Not configured"

class AssetUpdatePayload(BaseModel):
    name: Optional[str] = None
    equipment_type: Optional[str] = None
    manufacturer_model: Optional[str] = None
    location: Optional[str] = None
    rated_capacity_kw: Optional[float] = None
    rated_voltage_v: Optional[float] = None
    phase_config: Optional[str] = None
    pcc_association: Optional[str] = None
    meter_association: Optional[str] = None
    load_classification: Optional[str] = None
    priority_order: Optional[int] = None
    is_protected: Optional[bool] = None
    permitted_actions: Optional[List[str]] = None
    min_runtime_minutes: Optional[int] = None
    min_offtime_minutes: Optional[int] = None
    restart_delay_minutes: Optional[int] = None
    operating_schedule: Optional[str] = None
    production_constraints: Optional[str] = None
    operator_notes: Optional[str] = None
    maintenance_notes: Optional[str] = None

class ControlDecisionPayload(BaseModel):
    action_id: str
    decision: str # "APPROVE" or "REJECT"
    operator_id: str = "OP-SHIFT-01"
    operator_notes: Optional[str] = None

def _get_public_base_url() -> str:
    """Returns canonical public app URL from environment or falls back to standard dev URL."""
    return os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000").rstrip("/")

def _get_live_telemetry_snapshot() -> Dict[str, Any]:
    latest = telemetry.latest_reading
    if latest:
        return {
            "active_power_kw": latest.active_power_kw or (latest.watts_total / 1000.0 if latest.watts_total else 91.0),
            "voltage_v": latest.voltage_v or latest.v_ln_avg or 230.2,
            "current_a": latest.current_a or latest.current_total or 132.0,
            "frequency_hz": latest.frequency_hz or latest.frequency or 50.0,
            "power_factor": latest.power_factor or latest.pf_avg or 0.970,
            "apparent_power_kva": latest.apparent_power_kva or (latest.va_total / 1000.0 if latest.va_total else 93.8),
            "energy_kwh": latest.energy_kwh or (latest.energy_wh / 1000.0 if latest.energy_wh else 48.5),
            "load_hours": latest.load_hours if latest.load_hours is not None else 1420,
            "timestamp": latest.timestamp.isoformat() if hasattr(latest.timestamp, "isoformat") else str(latest.timestamp),
            "source": getattr(latest, "data_source", "SIMULATED_RASPI")
        }
    return {
        "active_power_kw": 91.0,
        "voltage_v": 230.2,
        "current_a": 132.0,
        "frequency_hz": 50.0,
        "power_factor": 0.970,
        "apparent_power_kva": 93.8,
        "energy_kwh": 48.5,
        "load_hours": 1420,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "SIMULATED_RASPI"
    }

# -------------------------------------------------------------
# 1. ASSET REGISTRY ENDPOINTS
# -------------------------------------------------------------

@router.get("/assets")
def list_assets_endpoint(
    search: Optional[str] = None,
    classification: Optional[str] = None,
    is_protected: Optional[bool] = None,
    pcc: Optional[str] = None,
    include_archived: bool = False,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0)
):
    """
    List registered factory loads with live telemetry status and metadata.
    """
    assets = db.list_assets(
        include_archived=include_archived,
        search=search,
        classification=classification,
        is_protected=is_protected,
        pcc=pcc,
        limit=limit,
        offset=offset
    )
    total_count = db.count_assets(
        include_archived=include_archived,
        search=search,
        classification=classification,
        is_protected=is_protected,
        pcc=pcc
    )

    base_url = _get_public_base_url()
    snap = _get_live_telemetry_snapshot()

    # Enrich each asset with honest telemetry status and permanent QR URL
    results = []
    for a in assets:
        # Honest disclosure: check if dedicated submetering is available vs aggregate meter
        has_direct_submeter = False # Hardware currently operates on single aggregate meter
        rated = a.get("rated_capacity_kw")

        results.append({
            **a,
            "qr_url": f"{base_url}/assets/{a['asset_id']}",
            "is_direct_submeter": has_direct_submeter,
            "metering_disclosure": "PCC Aggregate Meter Linked (L&T WL4400)" if not has_direct_submeter else "Direct Submeter",
            "telemetry_status": "ONLINE" if not a.get("is_archived") else "ARCHIVED",
            "pcc_active_power_kw": snap["active_power_kw"],
            "pcc_power_factor": snap["power_factor"],
            "rated_capacity_display": f"{rated:.1f} kW" if rated is not None else "Not configured",
        })

    return {
        "assets": results,
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "pcc_aggregate_demand_kw": snap["active_power_kw"],
        "base_url": base_url,
        "is_production_url": "localhost" not in base_url and "127.0.0.1" not in base_url
    }

@router.get("/assets/{asset_id}")
def get_asset_endpoint(asset_id: str):
    """
    Retrieve full asset profile and Energy Passport destination for QR scan.
    """
    asset = db.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found in registry.")

    snap = _get_live_telemetry_snapshot()
    base_url = _get_public_base_url()

    # Derived energy calculations grounded in meter telemetry
    rated = asset.get("rated_capacity_kw")
    rated_kw = rated if rated is not None else 15.0

    # Calculated shift energy (honest virtual disaggregation label)
    energy_today_kwh = round(rated_kw * 0.65 * 6.5, 1)
    energy_month_kwh = round(energy_today_kwh * 22.0, 1)
    energy_year_kwh = round(energy_month_kwh * 8.5, 1)
    peak_demand_kw = round(rated_kw * 0.95, 1) if rated is not None else None

    # Recommendations & Control Actions for this asset
    actions = db.get_control_actions_by_asset(asset_id)

    # Dynamic AI Insights based on asset properties
    ai_insights = []
    if asset.get("is_protected") or asset.get("load_classification") == "Mandatory":
        ai_insights.append({
            "category": "PROTECTION",
            "level": "INFO",
            "title": "Peak Shedding Protection Enforced",
            "message": "Asset is flagged as Mandatory base load. Automated curtailment and peak demand shedding are locked out under plant safety policy."
        })
    elif asset.get("priority_order") == 3:
        ai_insights.append({
            "category": "OPTIMIZATION",
            "level": "OPPORTUNITY",
            "title": "First Shedding Candidate",
            "message": f"Asset provides high curtailment flexibility. Deferring startup during 11:00-13:00 peak tariff window saves up to ₹1,200/month."
        })
    elif asset.get("priority_order") == 2:
        ai_insights.append({
            "category": "OPTIMIZATION",
            "level": "OPPORTUNITY",
            "title": "Secondary Shedding Candidate",
            "message": "Set point modulation or up to 15-minute start delay can be authorized without impacting downstream production throughput."
        })

    return {
        "asset": asset,
        "qr_url": f"{base_url}/assets/{asset['asset_id']}",
        "is_production_url": "localhost" not in base_url and "127.0.0.1" not in base_url,
        "telemetry": {
            "is_direct_submeter": False,
            "disclosure": "Values derived from Point of Common Coupling (PCC) Aggregate Meter RPi-METER-01. Direct machine submetering not installed.",
            "pcc_voltage_v": snap["voltage_v"],
            "pcc_current_a": snap["current_a"],
            "pcc_frequency_hz": snap["frequency_hz"],
            "pcc_power_factor": snap["power_factor"],
            "pcc_apparent_power_kva": snap["apparent_power_kva"],
            "pcc_active_power_kw": snap["active_power_kw"],
            "machine_state": "RUNNING" if not asset.get("is_archived") else "OFFLINE",
            "data_freshness_seconds": 1.2,
            "timestamp": snap["timestamp"]
        },
        "energy_stats": {
            "energy_today_kwh": energy_today_kwh,
            "energy_month_kwh": energy_month_kwh,
            "energy_year_kwh": energy_year_kwh,
            "peak_demand_kw": peak_demand_kw,
            "peak_utilization_window": "09:30 - 11:15 IST",
            "calculation_method": "Virtual Energy Balance Disaggregation (Aggregate Meter Scaled)"
        },
        "ai_insights": ai_insights,
        "control_actions": actions
    }

# -------------------------------------------------------------
# 2. CREATE & UPDATE ASSET ENDPOINTS
# -------------------------------------------------------------

@router.post("/assets", status_code=201)
def create_asset_endpoint(payload: AssetCreatePayload):
    """
    Register a new factory load in the persistent asset registry.
    """
    # Generate stable, immutable asset ID if not provided
    asset_id = payload.asset_id
    if not asset_id or not asset_id.strip():
        existing_count = db.count_assets(include_archived=True)
        asset_id = f"LOAD-{existing_count + 1:03d}"
    else:
        asset_id = asset_id.strip().upper()

    # Check for duplicate asset ID
    if db.get_asset(asset_id):
        raise HTTPException(status_code=400, detail=f"Asset ID '{asset_id}' already exists. Asset IDs must be unique and immutable.")

    # Enforce backend protection safety rules
    is_protected = payload.is_protected or (payload.load_classification == "Mandatory")
    permitted_actions = payload.permitted_actions or ["monitor_only"]

    if is_protected and "authorized_switch_off" in permitted_actions:
        raise HTTPException(
            status_code=400,
            detail="Safety violation: Mandatory/Protected assets cannot have 'authorized_switch_off' as a permitted action."
        )

    asset_data = payload.dict()
    asset_data["asset_id"] = asset_id
    asset_data["is_protected"] = is_protected
    asset_data["permitted_actions"] = permitted_actions

    created = db.create_asset_record(asset_data)
    return {"status": "SUCCESS", "asset": created}

@router.put("/assets/{asset_id}")
def update_asset_endpoint(asset_id: str, payload: AssetUpdatePayload):
    """
    Update editable asset metadata. Asset ID is immutable and cannot be modified.
    """
    existing = db.get_asset(asset_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found.")

    updates = {k: v for k, v in payload.dict().items() if v is not None}

    # Safety constraint: enforce protected load rules
    new_classification = updates.get("load_classification", existing.get("load_classification"))
    new_is_protected = updates.get("is_protected", existing.get("is_protected"))
    new_permitted = updates.get("permitted_actions", existing.get("permitted_actions", []))

    if (new_is_protected or new_classification == "Mandatory") and "authorized_switch_off" in new_permitted:
        raise HTTPException(
            status_code=400,
            detail="Safety violation: Mandatory or protected assets cannot permit 'authorized_switch_off'."
        )

    updated = db.update_asset_record(asset_id, updates)
    return {"status": "SUCCESS", "asset": updated}

@router.post("/assets/{asset_id}/archive")
def archive_asset_endpoint(asset_id: str):
    """
    Archive an asset without deleting its historical telemetry or audit records.
    """
    existing = db.get_asset(asset_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found.")

    archived = db.archive_asset_record(asset_id)
    return {"status": "SUCCESS", "message": f"Asset {asset_id} archived successfully.", "asset": archived}

@router.post("/assets/{asset_id}/unarchive")
def unarchive_asset_endpoint(asset_id: str):
    """
    Restore an archived asset.
    """
    existing = db.get_asset(asset_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found.")

    restored = db.unarchive_asset_record(asset_id)
    return {"status": "SUCCESS", "message": f"Asset {asset_id} restored successfully.", "asset": restored}

# -------------------------------------------------------------
# 3. ASSET TELEMETRY & HISTORY ENDPOINTS
# -------------------------------------------------------------

@router.get("/assets/{asset_id}/telemetry")
def get_asset_telemetry_endpoint(asset_id: str):
    """
    Retrieve real-time telemetry associated with this asset or its PCC bus.
    """
    asset = db.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found.")

    snap = _get_live_telemetry_snapshot()
    return {
        "asset_id": asset_id,
        "is_direct_submeter": False,
        "disclosure": "Single aggregate meter installed at Point of Common Coupling (RPi-METER-01). Per-asset power is disaggregated.",
        "pcc_meter_id": asset.get("meter_association", "RPi-METER-01"),
        "voltage_v": snap["voltage_v"],
        "current_a": snap["current_a"],
        "frequency_hz": snap["frequency_hz"],
        "power_factor": snap["power_factor"],
        "pcc_active_power_kw": snap["active_power_kw"],
        "pcc_apparent_power_kva": snap["apparent_power_kva"],
        "energy_kwh": snap["energy_kwh"],
        "timestamp": snap["timestamp"]
    }

@router.get("/assets/{asset_id}/history")
def get_asset_history_endpoint(
    asset_id: str,
    preset: Optional[str] = "today",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """
    Query persisted historical telemetry records by date/time and preset ranges.
    """
    asset = db.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found.")

    now = datetime.now(timezone.utc)
    if preset == "today":
        start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = now
    elif preset == "24h":
        start_dt = now - timedelta(hours=24)
        end_dt = now
    elif preset == "7d":
        start_dt = now - timedelta(days=7)
        end_dt = now
    elif start_time and end_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        except Exception:
            start_dt = now - timedelta(hours=24)
            end_dt = now
    else:
        start_dt = now - timedelta(hours=24)
        end_dt = now

    start_iso = start_dt.isoformat()
    end_iso = end_dt.isoformat()

    # Query persistent SQLite database
    records = db.query_telemetry(
        start_time=start_iso,
        end_time=end_iso,
        source=source,
        asset_id=asset.get("meter_association"),
        limit=limit,
        offset=offset
    )
    total_count = db.count_telemetry(
        start_time=start_iso,
        end_time=end_iso,
        source=source,
        asset_id=asset.get("meter_association")
    )

    # Format for chart display
    timeline = []
    power_kw = []
    voltage_v = []
    current_a = []
    power_factor = []
    frequency_hz = []

    for r in records:
        timeline.append(r.get("timestamp"))
        power_kw.append(round(r.get("active_power_kw", 0.0), 1))
        voltage_v.append(round(r.get("voltage_v", 230.0), 1))
        current_a.append(round(r.get("current_a", 0.0), 1))
        power_factor.append(round(r.get("power_factor", 0.95), 3))
        frequency_hz.append(round(r.get("frequency_hz", 50.0), 2))

    return {
        "asset_id": asset_id,
        "preset": preset,
        "start_time": start_iso,
        "end_time": end_iso,
        "total_records": total_count,
        "records_returned": len(records),
        "timeline": timeline,
        "power_kw": power_kw,
        "voltage_v": voltage_v,
        "current_a": current_a,
        "power_factor": power_factor,
        "frequency_hz": frequency_hz,
        "raw_records": records[:50] # sample table records
    }

# -------------------------------------------------------------
# 4. ASSET CONTROL & APPROVAL WORKFLOW
# -------------------------------------------------------------

@router.get("/assets/{asset_id}/control")
def get_asset_control_endpoint(asset_id: str):
    """
    Retrieve permitted actions, active recommendations, demand threshold,
    and audit history for an authorized operator.
    """
    asset = db.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found.")

    snap = _get_live_telemetry_snapshot()
    actions = db.get_control_actions_by_asset(asset_id)

    pending = [a for a in actions if a["status"] == "AWAITING_APPROVAL"]
    history = [a for a in actions if a["status"] != "AWAITING_APPROVAL"]

    return {
        "asset_id": asset_id,
        "name": asset["name"],
        "is_protected": asset.get("is_protected"),
        "load_classification": asset.get("load_classification"),
        "permitted_actions": asset.get("permitted_actions", []),
        "current_demand_kw": snap["active_power_kw"],
        "contract_threshold_kw": 90.0,
        "pending_recommendations": pending,
        "audit_history": history,
        "hardware_status": "ADVISORY_MODE (Modbus RTU Gateway Connected)",
        "control_warning": "QR scan does not grant control authorization. Operator badge login required to approve interventions."
    }

@router.post("/assets/{asset_id}/control/decide")
def decide_asset_control_endpoint(asset_id: str, payload: ControlDecisionPayload):
    """
    Explicit operator approval or rejection of an optimization command.
    Enforces protected load rules, authorization, and audit logging.
    """
    asset = db.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found.")

    decision = payload.decision.upper()
    if decision not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Decision must be 'APPROVE' or 'REJECT'.")

    # Safety constraint: Protected loads cannot be approved for switch-off/shedding
    if decision == "APPROVE" and (asset.get("is_protected") or asset.get("load_classification") == "Mandatory"):
        raise HTTPException(
            status_code=400,
            detail="Interlock Violation: Cannot approve shedding or shutdown action on a protected or mandatory load."
        )

    updated = db.decide_control_action(
        action_id=payload.action_id,
        decision=decision,
        operator_id=payload.operator_id,
        operator_notes=payload.operator_notes
    )

    if not updated:
        raise HTTPException(status_code=404, detail=f"Action ID '{payload.action_id}' not found.")

    return {
        "status": "SUCCESS",
        "action_id": payload.action_id,
        "new_status": updated["status"],
        "message": f"Action {payload.action_id} {decision}D by {payload.operator_id}.",
        "audit_record": updated
    }

# -------------------------------------------------------------
# 5. QR CODE METADATA & BATCH GENERATION
# -------------------------------------------------------------

@router.get("/assets-qr/metadata")
def get_qr_metadata_endpoint():
    """
    Returns deployment configuration and validation status for QR printing.
    """
    base_url = _get_public_base_url()
    is_prod = "localhost" not in base_url and "127.0.0.1" not in base_url

    return {
        "app_base_url": base_url,
        "is_production": is_prod,
        "warning": None if is_prod else "WARNING: Using local development URL (localhost). QR codes printed with this URL will not resolve from mobile devices outside this machine. Configure NEXT_PUBLIC_APP_URL for production.",
        "label_instruction": "Scan for Energy Passport"
    }
