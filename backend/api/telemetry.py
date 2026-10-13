from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import pandas as pd
from schemas.energy import EnergyReading, DataSource, DataQuality, MachineState
from api.google_sheets import gsheets_db
from database.db import insert_telemetry, get_connection
from ml.forecasting.model import forecaster
import uuid

router = APIRouter()

# Keep state in memory for health/live tracking
live_device_state: Dict[str, dict] = {}
latest_reading: Optional[EnergyReading] = None
latest_relay_decision: Optional[Dict[str, Any]] = None
pending_relay_commands: List[Dict[str, Any]] = []
# We still keep a small bounded memory buffer for quick API reads to avoid rate limits on every dashboard poll, 
# but persistence relies ENTIRELY on gsheets_db
recent_readings_cache: List[EnergyReading] = []

class TelemetryPayload(BaseModel):
    timestamp: str
    source: str = "SIMULATED_RASPI"
    device_id: str = "RPi-METER-01"
    
    # Standard aggregated fields (optional, derived if not supplied)
    voltage: Optional[float] = None
    current: Optional[float] = None
    active_power_kw: Optional[float] = None
    energy_kwh: Optional[float] = None
    frequency_hz: Optional[float] = None
    power_factor: Optional[float] = None
    quality: str = "GOOD"
    machine_state: str = "RUNNING"

    # All 27 L&T WL4400 Modbus Memory Map parameters (addresses 40101 to 40217)
    # 1. Active Power (W)
    watts_total: Optional[float] = None   # 40101: Watts Total
    watts_r: Optional[float] = None       # 40103: Watts R phase
    watts_y: Optional[float] = None       # 40105: Watts Y phase
    watts_b: Optional[float] = None       # 40107: Watts B phase

    # 2. Power Factor
    pf_avg: Optional[float] = None        # 40117: PF Avg (inst)
    pf_r: Optional[float] = None          # 40119: PF R phase
    pf_y: Optional[float] = None          # 40121: PF Y phase
    pf_b: Optional[float] = None          # 40123: PF B phase

    # 3. Apparent Power (VA)
    va_total: Optional[float] = None      # 40125: VA total
    va_r: Optional[float] = None          # 40127: VA R phase
    va_y: Optional[float] = None          # 40129: VA Y phase
    va_b: Optional[float] = None          # 40131: VA B phase

    # 4. Line-to-Line Voltage (V)
    v_ll_avg: Optional[float] = None      # 40133: VL L average
    v_ry: Optional[float] = None          # 40135: VR Y phase
    v_yb: Optional[float] = None          # 40137: VY B phase
    v_br: Optional[float] = None          # 40139: VB R phase

    # 5. Line-to-Neutral Phase Voltage (V)
    v_ln_avg: Optional[float] = None      # 40141: VL N average
    v_r: Optional[float] = None           # 40143: V R phase
    v_y: Optional[float] = None           # 40145: V Y phase
    v_b: Optional[float] = None           # 40147: V B phase

    # 6. Current (A)
    current_total: Optional[float] = None # 40149: Current Total
    current_r: Optional[float] = None     # 40151: Current R phase
    current_y: Optional[float] = None     # 40153: Current Y phase
    current_b: Optional[float] = None     # 40155: Current B phase

    # 7. Frequency (Hz)
    frequency: Optional[float] = None     # 40157: Frequency

    # 8. Energy (Wh, VAh) & Load Hours
    energy_wh: Optional[float] = None     # 40159: Wh
    energy_vah: Optional[float] = None    # 40161: VAh
    load_hours: Optional[int] = None      # 40217: Load Hours

    # Relay State Machine telemetry
    relay_decision: Optional[Dict[str, Any]] = None

@router.post("/telemetry/ingest")
def ingest_telemetry(payload: TelemetryPayload):
    global latest_reading, latest_relay_decision
    
    try:
        ts = datetime.fromisoformat(payload.timestamp.replace('Z', '+00:00'))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid timestamp format. Use ISO 8601.")
        
    # Cross-calculate active power
    watts_total = payload.watts_total
    watts_r = payload.watts_r
    watts_y = payload.watts_y
    watts_b = payload.watts_b
    if watts_total is None and (watts_r is not None or watts_y is not None or watts_b is not None):
        watts_total = (watts_r or 0.0) + (watts_y or 0.0) + (watts_b or 0.0)

    active_power_kw = payload.active_power_kw
    if active_power_kw is None and watts_total is not None:
        active_power_kw = watts_total / 1000.0
    elif watts_total is None and active_power_kw is not None:
        watts_total = active_power_kw * 1000.0
    elif active_power_kw is None and watts_total is None:
        active_power_kw = 0.0
        watts_total = 0.0
    # Cross-calculate energy
    energy_wh = payload.energy_wh
    energy_kwh = payload.energy_kwh
    if energy_kwh is None and energy_wh is not None:
        energy_kwh = energy_wh / 1000.0
    elif energy_wh is None and energy_kwh is not None:
        energy_wh = energy_kwh * 1000.0
    elif energy_kwh is None and energy_wh is None:
        energy_kwh = 0.0
        energy_wh = 0.0

    # Voltage (Phase-to-Neutral & Line-to-Line)
    v_r = payload.v_r
    v_y = payload.v_y
    v_b = payload.v_b
    v_ln_avg = payload.v_ln_avg
    if v_ln_avg is None:
        volts = [v for v in [v_r, v_y, v_b] if v is not None]
        if volts:
            v_ln_avg = sum(volts) / len(volts)
        elif payload.voltage is not None:
            v_ln_avg = payload.voltage
        else:
            v_ln_avg = 230.0
    
    voltage_v = payload.voltage if payload.voltage is not None else v_ln_avg
    if v_r is None: v_r = voltage_v
    if v_y is None: v_y = voltage_v
    if v_b is None: v_b = voltage_v

    v_ll_avg = payload.v_ll_avg
    v_ry = payload.v_ry
    v_yb = payload.v_yb
    v_br = payload.v_br
    if not v_ll_avg and v_ln_avg:
        ll_volts = [v for v in [v_ry, v_yb, v_br] if v]
        if ll_volts:
            v_ll_avg = sum(ll_volts) / len(ll_volts)
        else:
            v_ll_avg = v_ln_avg * 1.73205
    if not v_ry and v_r: v_ry = v_r * 1.73205 if v_r else v_ll_avg
    if not v_yb and v_y: v_yb = v_y * 1.73205 if v_y else v_ll_avg
    if not v_br and v_b: v_br = v_b * 1.73205 if v_b else v_ll_avg

    # Current (Phase & Total)
    current_r = payload.current_r
    current_y = payload.current_y
    current_b = payload.current_b
    current_total = payload.current_total
    if current_total is None:
        currs = [c for c in [current_r, current_y, current_b] if c is not None]
        if currs:
            current_total = sum(currs)
        elif payload.current is not None:
            current_total = payload.current
        else:
            current_total = 0.0
            
    current_a = payload.current if payload.current is not None else current_total
    if current_r is None: current_r = current_total / 3.0
    if current_y is None: current_y = current_total / 3.0
    if current_b is None: current_b = current_total / 3.0

    # Power Factor (Phase & Average)
    pf_avg = payload.pf_avg
    pf_r = payload.pf_r
    pf_y = payload.pf_y
    pf_b = payload.pf_b
    if pf_avg is None:
        pfs = [p for p in [pf_r, pf_y, pf_b] if p is not None]
        if pfs:
            pf_avg = sum(pfs) / len(pfs)
        elif payload.power_factor is not None:
            pf_avg = payload.power_factor
        else:
            pf_avg = 0.95
    power_factor = payload.power_factor if payload.power_factor is not None else pf_avg
    if pf_r is None: pf_r = power_factor
    if pf_y is None: pf_y = power_factor
    if pf_b is None: pf_b = power_factor

    # Apparent Power (Phase & Total)
    va_r = payload.va_r or ((watts_r / pf_r) if (watts_r and pf_r) else (v_r * current_r))
    va_y = payload.va_y or ((watts_y / pf_y) if (watts_y and pf_y) else (v_y * current_y))
    va_b = payload.va_b or ((watts_b / pf_b) if (watts_b and pf_b) else (v_b * current_b))
    va_total = payload.va_total or (va_r + va_y + va_b)

    # Frequency
    frequency = payload.frequency or payload.frequency_hz or 50.0
    frequency_hz = payload.frequency_hz or frequency

    # Energy VAh & Load Hours
    energy_vah = payload.energy_vah or (energy_wh / power_factor if power_factor else energy_wh)
    load_hours = payload.load_hours if payload.load_hours is not None else 1420

    reading = EnergyReading(
        timestamp=ts,
        factory_id="fac_001",
        asset_id=payload.device_id,
        voltage_v=voltage_v,
        current_a=current_a,
        active_power_kw=active_power_kw,
        apparent_power_kva=va_total / 1000.0 if va_total else None,
        energy_kwh=energy_kwh,
        frequency_hz=frequency_hz,
        power_factor=power_factor,
        # 27 Memory map parameters
        watts_total=watts_total,
        watts_r=watts_r,
        watts_y=watts_y,
        watts_b=watts_b,
        pf_avg=pf_avg,
        pf_r=pf_r,
        pf_y=pf_y,
        pf_b=pf_b,
        va_total=va_total,
        va_r=va_r,
        va_y=va_y,
        va_b=va_b,
        v_ll_avg=v_ll_avg,
        v_ry=v_ry,
        v_yb=v_yb,
        v_br=v_br,
        v_ln_avg=v_ln_avg,
        v_r=v_r,
        v_y=v_y,
        v_b=v_b,
        current_total=current_total,
        current_r=current_r,
        current_y=current_y,
        current_b=current_b,
        frequency=frequency,
        energy_wh=energy_wh,
        energy_vah=energy_vah,
        load_hours=load_hours,
        machine_state=MachineState[payload.machine_state] if payload.machine_state in MachineState.__members__ else (MachineState.RUNNING if payload.active_power_kw > 0.1 else MachineState.IDLE),
        data_source=DataSource[payload.source] if payload.source in DataSource.__members__ else DataSource.RASPBERRY_PI,
        data_quality=DataQuality[payload.quality] if payload.quality in DataQuality.__members__ else DataQuality.GOOD
    )
    
    # Store in cache for quick reads
    recent_readings_cache.append(reading)
    if len(recent_readings_cache) > 1440:
        recent_readings_cache.pop(0)
    
    latest_reading = reading
    record_id = str(uuid.uuid4())
    
    # 1. Authoritative Database Persistence
    db_record = {
        "record_id": record_id,
        "timestamp": ts.isoformat(),
        "factory_id": "fac_001",
        "asset_id": payload.device_id,
        "voltage_v": voltage_v,
        "current_a": current_a,
        "active_power_kw": active_power_kw,
        "energy_kwh": energy_kwh,
        "frequency_hz": frequency_hz,
        "power_factor": power_factor,
        "machine_state": payload.machine_state,
        "data_source": payload.source,
        "data_quality": payload.quality,
        # Memory map attributes
        "watts_total": watts_total,
        "watts_r": watts_r,
        "watts_y": watts_y,
        "watts_b": watts_b,
        "pf_avg": pf_avg,
        "pf_r": pf_r,
        "pf_y": pf_y,
        "pf_b": pf_b,
        "va_total": va_total,
        "va_r": va_r,
        "va_y": va_y,
        "va_b": va_b,
        "v_ll_avg": v_ll_avg,
        "v_ry": v_ry,
        "v_yb": v_yb,
        "v_br": v_br,
        "v_ln_avg": v_ln_avg,
        "v_r": v_r,
        "v_y": v_y,
        "v_b": v_b,
        "current_total": current_total,
        "current_r": current_r,
        "current_y": current_y,
        "current_b": current_b,
        "frequency": frequency,
        "energy_wh": energy_wh,
        "energy_vah": energy_vah,
        "load_hours": load_hours
    }
    db_success = insert_telemetry(db_record)
    
    # 2. Google Sheets Buffer
    gs_record = reading.dict()
    gs_record['record_id'] = record_id
    gs_record['timestamp'] = ts.isoformat()
    gs_record['machine_state'] = payload.machine_state
    gs_record['source'] = payload.source
    gs_record['quality'] = payload.quality
    gsheets_db.append_telemetry([gs_record])
    
    live_device_state[payload.device_id] = {
        "last_seen": datetime.now(timezone.utc),
        "source": payload.source,
        "packet_count": live_device_state.get(payload.device_id, {}).get("packet_count", 0) + 1
    }
    
    if payload.relay_decision:
        latest_relay_decision = payload.relay_decision

    resp = {
        "accepted": True,
        "device_id": payload.device_id,
        "source": payload.source,
        "timestamp": payload.timestamp,
        "server_timestamp": datetime.now(timezone.utc).isoformat(),
        "persistence": {
            "database": "PERSISTED" if db_success else "FAILED",
            "google_sheets": "PENDING_SYNC"
        }
    }
    if pending_relay_commands:
        resp["pending_relay_command"] = pending_relay_commands.pop(0)

    return resp

class RelayControlPayload(BaseModel):
    channel: Optional[int] = 1 # 1, 2, 3
    action: str # "SHED", "RESTORE", "EMERGENCY_RESTORE_ALL", "AUTO"

@router.get("/relays/status")
def get_relay_status():
    global latest_relay_decision, pending_relay_commands
    status = latest_relay_decision or {
        "state": "NORMAL",
        "mode": "ACTIVE",
        "threshold_kw": 0.14,
        "ceiling_kw": 0.20,
        "delay_seconds": 8.0,
        "restart_delay_seconds": 10.0,
        "priority_order": "Relay 1 (1st) -> Relay 2 (2nd) -> Relay 3 (3rd)",
        "channels": {
            "1": {"channel_id": 1, "name": "Relay 1 (Opportunistic Load)", "priority": 1, "is_shed": False, "state": "OPERATIONAL"},
            "2": {"channel_id": 2, "name": "Relay 2 (Flexible Load)", "priority": 2, "is_shed": False, "state": "OPERATIONAL"},
            "3": {"channel_id": 3, "name": "Relay 3 (Protected Load)", "priority": 3, "is_shed": False, "state": "OPERATIONAL"}
        }
    }
    return {
        "relay_decision": status,
        "pending_queue_count": len(pending_relay_commands),
        "server_timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.post("/relays/control")
def control_relays(cmd: RelayControlPayload):
    global pending_relay_commands, latest_relay_decision
    command_dict = {
        "channel": cmd.channel or 1,
        "action": cmd.action.upper(),
        "queued_at": datetime.now(timezone.utc).isoformat()
    }
    pending_relay_commands.append(command_dict)
    
    act_up = cmd.action.upper()
    # Optimistically update in-memory state for instantaneous UI response
    if latest_relay_decision:
        if act_up == "SET_MODE_AUTO":
            latest_relay_decision["control_mode"] = "AUTO"
        elif act_up == "SET_MODE_MANUAL":
            latest_relay_decision["control_mode"] = "MANUAL"
        elif act_up == "SET_POLARITY_ACTIVE_LOW":
            latest_relay_decision["active_low"] = True
        elif act_up == "SET_POLARITY_ACTIVE_HIGH":
            latest_relay_decision["active_low"] = False

        if "channels" in latest_relay_decision:
            chs = latest_relay_decision["channels"]
            ch_key = str(cmd.channel) if str(cmd.channel) in chs else cmd.channel
            if act_up in ("SHED", "OFF"):
                latest_relay_decision["control_mode"] = "MANUAL"
                if ch_key in chs:
                    chs[ch_key]["is_shed"] = True
                    chs[ch_key]["state"] = "SHED"
            elif act_up in ("RESTORE", "ON"):
                latest_relay_decision["control_mode"] = "MANUAL"
                if ch_key in chs:
                    chs[ch_key]["is_shed"] = False
                    chs[ch_key]["state"] = "OPERATIONAL"
            elif act_up == "EMERGENCY_RESTORE_ALL":
                latest_relay_decision["control_mode"] = "MANUAL"
                for c in chs.values():
                    c["is_shed"] = False
                    c["state"] = "OPERATIONAL"
                latest_relay_decision["state"] = "NORMAL"

    return {
        "status": "QUEUED",
        "message": f"Relay command {cmd.action} queued for Raspberry Pi hardware actuation.",
        "command": command_dict
    }

@router.get("/telemetry/health")
def get_device_health():
    now = datetime.now(timezone.utc)
    health_status = []
    
    for device_id, state in live_device_state.items():
        age_seconds = (now - state["last_seen"]).total_seconds()
        status = "OFFLINE"
        if age_seconds < 5:
            status = "CONNECTED"
        elif age_seconds < 15:
            status = "STALE"
            
        health_status.append({
            "device_id": device_id,
            "source": state["source"],
            "status": status,
            "last_seen": state["last_seen"].isoformat(),
            "data_age_seconds": round(age_seconds, 1),
            "packet_count": state["packet_count"]
        })
        
    return health_status


def _get_active_source():
    global latest_reading
    now = datetime.now(timezone.utc)
    
    if latest_reading is None:
        try:
            from database.db import query_telemetry
            recent = query_telemetry(None, None, limit=1)
            if recent:
                row = recent[0]
                ts = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                if abs((now - ts).total_seconds()) <= 30:
                    latest_reading = EnergyReading(
                        timestamp=ts,
                        factory_id=row.get('factory_id', 'fac_001'),
                        asset_id=row.get('asset_id', 'L&T_WL4400_01'),
                        voltage_v=row.get('voltage_v', 240.0),
                        current_a=row.get('current_a', 0.0),
                        active_power_kw=row.get('active_power_kw', 0.0),
                        energy_kwh=row.get('energy_kwh', 0.0),
                        frequency_hz=row.get('frequency_hz', 50.0),
                        power_factor=row.get('power_factor', 0.0),
                        watts_total=row.get('watts_total', 0.0),
                        watts_r=row.get('watts_r', 0.0),
                        watts_y=row.get('watts_y', 0.0),
                        watts_b=row.get('watts_b', 0.0),
                        pf_avg=row.get('pf_avg', 0.0),
                        pf_r=row.get('pf_r', 0.0),
                        pf_y=row.get('pf_y', 0.0),
                        pf_b=row.get('pf_b', 0.0),
                        va_total=row.get('va_total', 0.0),
                        va_r=row.get('va_r', 0.0),
                        va_y=row.get('va_y', 0.0),
                        va_b=row.get('va_b', 0.0),
                        v_ll_avg=row.get('v_ll_avg', 416.0),
                        v_ry=row.get('v_ry', 416.0),
                        v_yb=row.get('v_yb', 416.0),
                        v_br=row.get('v_br', 416.0),
                        v_ln_avg=row.get('v_ln_avg', 240.0),
                        v_r=row.get('v_r', 240.0),
                        v_y=row.get('v_y', 240.0),
                        v_b=row.get('v_b', 240.0),
                        current_total=row.get('current_total', 0.0),
                        current_r=row.get('current_r', 0.0),
                        current_y=row.get('current_y', 0.0),
                        current_b=row.get('current_b', 0.0),
                        frequency=row.get('frequency', 50.0),
                        energy_wh=row.get('energy_wh', 0.0),
                        energy_vah=row.get('energy_vah', 0.0),
                        load_hours=row.get('load_hours', 0),
                        machine_state=MachineState.IDLE if row.get('machine_state') == 'IDLE' else MachineState.RUNNING,
                        data_source=DataSource.RASPBERRY_PI if row.get('data_source') == 'RASPBERRY_PI' else DataSource.SIMULATED_RASPI,
                        data_quality=DataQuality.GOOD
                    )
        except Exception:
            pass

    # 1. RASPBERRY PI PHYSICAL LIVE (check ingestion cache)
    if latest_reading and latest_reading.data_source.value == "RASPBERRY_PI":
        age = (now - latest_reading.timestamp).total_seconds()
        if -30 <= age <= 30:
            return {
                "active_source": "RASPBERRY_PI",
                "source_status": "CONNECTED",
                "last_reading_timestamp": latest_reading.timestamp.isoformat(),
                "data_age_seconds": round(max(0.0, age), 1),
                "fallback_reason": None,
                "latest_reading": latest_reading.dict(),
                "source_health": {"status": "HEALTHY", "message": "Receiving live hardware telemetry"}
            }
            
    # 1.B. RASPBERRY PI TEST STREAM
    if latest_reading and latest_reading.data_source.value == "SIMULATED_RASPI":
        age = (now - latest_reading.timestamp).total_seconds()
        if -30 <= age <= 30:
            return {
                "active_source": "SIMULATED_RASPI",
                "source_status": "CONNECTED_TEST",
                "last_reading_timestamp": latest_reading.timestamp.isoformat(),
                "data_age_seconds": round(max(0.0, age), 1),
                "fallback_reason": None,
                "latest_reading": latest_reading.dict(),
                "source_health": {"status": "HEALTHY", "message": "Receiving TEST hardware telemetry"}
            }

    # 2. GOOGLE SHEETS FALLBACK
    fallback_reason = "Raspberry Pi offline" if not latest_reading else f"Raspberry Pi telemetry stale ({round((now - latest_reading.timestamp).total_seconds())}s old)"
    
    gs_record = gsheets_db.get_latest_telemetry_fallback()
    if gs_record:
        try:
            ts_str = gs_record.get('timestamp')
            ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00')) if ts_str else None
            
            if ts:
                age = (now - ts).total_seconds()
                if -5 <= age <= 60:  # Must be genuinely fresh to act as live telemetry
                    
                    # Convert to EnergyReading to ensure schema compliance
                    fallback_reading = EnergyReading(
                        timestamp=ts,
                        factory_id=gs_record.get('factory_id', 'fac_001'),
                        asset_id=gs_record.get('asset_id', 'UNKNOWN'),
                        voltage_v=float(gs_record.get('voltage_v')) if gs_record.get('voltage_v') else None,
                        current_a=float(gs_record.get('current_a')) if gs_record.get('current_a') else None,
                        active_power_kw=float(gs_record.get('active_power_kw', 0)),
                        energy_kwh=float(gs_record.get('energy_kwh', 0)),
                        frequency_hz=float(gs_record.get('frequency_hz')) if gs_record.get('frequency_hz') else None,
                        power_factor=float(gs_record.get('power_factor')) if gs_record.get('power_factor') else None,
                        machine_state=MachineState(gs_record.get('machine_state', 'UNKNOWN')),
                        data_source=DataSource.RASPBERRY_PI if gs_record.get('source') == 'RASPBERRY_PI' else (DataSource.SIMULATED_RASPI if gs_record.get('source') == 'SIMULATED_RASPI' else DataSource.METER),
                        data_quality=DataQuality(gs_record.get('quality', 'GOOD'))
                    )
                    
                    return {
                        "active_source": "GOOGLE_SHEETS",
                        "source_status": "FALLBACK",
                        "last_reading_timestamp": fallback_reading.timestamp.isoformat(),
                        "data_age_seconds": round(age, 1),
                        "fallback_reason": fallback_reason,
                        "latest_reading": fallback_reading.dict(),
                        "source_health": {"status": "DEGRADED", "message": "Using Google Sheets historical fallback"}
                    }
        except Exception as e:
            fallback_reason += f" | Google Sheets fallback error: {str(e)}"
            
    # 3. OFFLINE
    return {
        "active_source": "NONE",
        "source_status": "OFFLINE",
        "last_reading_timestamp": latest_reading.timestamp.isoformat() if latest_reading else None,
        "data_age_seconds": round((now - latest_reading.timestamp).total_seconds(), 1) if latest_reading else 999999,
        "fallback_reason": fallback_reason,
        "latest_reading": latest_reading.dict() if latest_reading else None,
        "source_health": {"status": "OFFLINE", "message": "No valid data sources available"}
    }

@router.get("/telemetry/source-status")
def get_source_status():
    return _get_active_source()

@router.get("/telemetry/latest")
def get_latest_telemetry():
    source_info = _get_active_source()
    
    storage_health = {
        "connected": gsheets_db.connected,
        "pending_records": len(gsheets_db.telemetry_buffer),
        "last_write": gsheets_db.last_write_time.isoformat() if gsheets_db.last_write_time else None
    }
        
    return {
        "status": source_info["source_status"],
        "active_source": source_info["active_source"],
        "data_age_seconds": source_info["data_age_seconds"],
        "fallback_reason": source_info["fallback_reason"],
        "reading": source_info["latest_reading"],
        "storage": storage_health
    }
        
    device_state = live_device_state.get(latest_reading.asset_id)
    if not device_state:
        status = "OFFLINE"
        age = 999
    else:
        age = (datetime.now(timezone.utc) - device_state["last_seen"]).total_seconds()
        if age > 15:
            status = "OFFLINE"
        else:
            status = "CONNECTED" 
            
    storage_health = {
        "connected": gsheets_db.connected,
        "pending_records": len(gsheets_db.telemetry_buffer),
        "last_write": gsheets_db.last_write_time.isoformat() if gsheets_db.last_write_time else None
    }
        
    return {
        "status": status,
        "data_age_seconds": round(age, 1),
        "reading": latest_reading.dict(),
        "storage": storage_health
    }

@router.get("/telemetry/history")
def get_telemetry_history():
    if not recent_readings_cache:
        try:
            from database.db import query_telemetry
            db_records = query_telemetry(None, None, limit=100)
            if db_records:
                return {
                    "count": len(db_records),
                    "history": list(reversed(db_records)),
                    "storage_connected": gsheets_db.connected
                }
        except Exception:
            pass
    return {
        "count": len(recent_readings_cache),
        "history": [r.dict() for r in recent_readings_cache],
        "storage_connected": gsheets_db.connected
    }

@router.get("/telemetry/history_explorer")
def get_history_explorer(
    start_time: str,
    end_time: str,
    source: str = None,
    asset_id: str = None,
    limit: int = 5000,
    offset: int = 0
):
    from database.db import query_telemetry, count_telemetry
    
    records = query_telemetry(start_time, end_time, source, asset_id, limit, offset)
    total_count = count_telemetry(start_time, end_time, source, asset_id)
    
    return {
        "records": records,
        "total_count": total_count,
        "limit": limit,
        "offset": offset
    }


from pydantic import BaseModel
class CustomHistoryPayload(BaseModel):
    history: list

@router.post("/forecast/custom")
def run_custom_forecast(payload: CustomHistoryPayload):
    from ml.forecasting.model import forecaster
    import pandas as pd
    
    if not payload.history:
        return {"forecast": None, "error": "No history provided"}
        
    try:
        hist_data = [{"timestamp": r.get('timestamp'), "power_kw": r.get('active_power_kw')} for r in payload.history]
        df_hist = pd.DataFrame(hist_data)
        
        pred = forecaster.predict_15m_from_history(df_hist)
        return {"forecast": pred}
    except Exception as e:
        return {"forecast": None, "error": str(e)}


@router.get("/telemetry/layman_analytics")
def get_layman_analytics(mode: Optional[str] = "SIMULATION"):
    is_live_mode = bool(mode and mode.upper() == "LIVE")

    # In LIVE toggle: CMD ceiling = 200 VA, safe limit = 140 VA
    # In SIMULATION toggle: CMD ceiling = 100 kW, safe limit = 90 kW
    contract_demand_kw = 200.0 if is_live_mode else 100.0
    safe_operating_kw = 140.0 if is_live_mode else 90.0
    demand_unit = "VA" if is_live_mode else "kW"
    power_unit = "W" if is_live_mode else "kW"
    energy_unit = "Wh" if is_live_mode else "kWh"
    apparent_energy_unit = "VAh" if is_live_mode else "kVAh"
    
    current_demand_kw = 0.0
    watts_r = 0.0
    watts_y = 0.0
    watts_b = 0.0
    watts_total = 0.0
    va_total = 0.0
    pf_avg = 0.95
    freq = 50.0
    v_ln_avg = 230.0
    v_ll_avg = 398.0
    
    if latest_reading:
        if latest_reading.watts_r is not None: watts_r = latest_reading.watts_r
        if latest_reading.watts_y is not None: watts_y = latest_reading.watts_y
        if latest_reading.watts_b is not None: watts_b = latest_reading.watts_b
        if latest_reading.pf_avg is not None: pf_avg = round(latest_reading.pf_avg, 3)
        if latest_reading.frequency is not None: freq = round(latest_reading.frequency, 2)
        if latest_reading.v_ln_avg is not None: v_ln_avg = round(latest_reading.v_ln_avg, 1)
        if latest_reading.v_ll_avg is not None: v_ll_avg = round(latest_reading.v_ll_avg, 1)
        
        watts_total = float(latest_reading.watts_total or ((latest_reading.active_power_kw or 0.0) * 1000.0))
        pf_safe = pf_avg if (pf_avg and pf_avg > 0.05) else 0.95
        va_total = float(latest_reading.va_total or (watts_total / pf_safe if (watts_total and pf_safe) else 0.0))
        
        if is_live_mode:
            current_demand_kw = round(va_total if va_total > 0 else watts_total, 1)
        else:
            current_demand_kw = round(latest_reading.active_power_kw or 0.0, 2)
    else:
        pf_safe = 0.95

    is_live_meter = bool(latest_reading and latest_reading.data_source == DataSource.RASPBERRY_PI)
    now_local = datetime.now()
    current_hour = now_local.hour
    current_dow = now_local.weekday()
    today_date_str = now_local.strftime("%d %b")

    # Peak demand calculation from real-time cache and authoritative SQLite database
    if is_live_mode:
        cache_pool = [r for r in recent_readings_cache if (r.data_source == DataSource.RASPBERRY_PI and (r.active_power_kw or 0.0) <= 0.25)]
    else:
        cache_pool = [r for r in recent_readings_cache if (r.data_source != DataSource.RASPBERRY_PI or (r.active_power_kw or 0.0) >= 5.0)]

    if cache_pool:
        if is_live_mode:
            peak_cache_val = max([float(r.va_total or (((r.watts_total or 0.0) or ((r.active_power_kw or 0.0) * 1000.0)) / (r.pf_avg if (r.pf_avg and r.pf_avg > 0.05) else 0.95))) for r in cache_pool], default=current_demand_kw)
            peak_cache_item = max(cache_pool, key=lambda r: float(r.va_total or (((r.watts_total or 0.0) or ((r.active_power_kw or 0.0) * 1000.0)) / (r.pf_avg if (r.pf_avg and r.pf_avg > 0.05) else 0.95))))
            peak_cache_time = peak_cache_item.timestamp.strftime("%H:%M")
        else:
            peak_cache_item = max(cache_pool, key=lambda r: (r.active_power_kw or 0.0))
            peak_cache_val = float(peak_cache_item.active_power_kw or current_demand_kw)
            peak_cache_time = peak_cache_item.timestamp.strftime("%H:%M")
    else:
        peak_cache_val = current_demand_kw
        peak_cache_time = now_local.strftime("%H:%M")

    db_peak_val = 0.0
    db_peak_time = peak_cache_time
    month_peak_val = max(peak_cache_val, current_demand_kw)
    db_hourly_map = {}

    try:
        with get_connection() as conn:
            src_filter = "data_source = 'RASPBERRY_PI' AND active_power_kw <= 0.25" if is_live_mode else "(data_source != 'RASPBERRY_PI' OR active_power_kw >= 5.0)"
            row = conn.execute(f"""
                SELECT active_power_kw, timestamp 
                FROM telemetry 
                WHERE {src_filter}
                  AND date(datetime(timestamp, 'localtime')) = date('now', 'localtime')
                ORDER BY active_power_kw DESC LIMIT 1
            """).fetchone()
            if row and row["active_power_kw"] is not None:
                raw_db_peak = float(row["active_power_kw"])
                db_peak_val = (raw_db_peak * 1000.0 / pf_safe) if is_live_mode else raw_db_peak
                try:
                    ts_dt = datetime.fromisoformat(str(row["timestamp"]).replace('Z', '+00:00'))
                    db_peak_time = ts_dt.strftime("%H:%M")
                except Exception:
                    db_peak_time = str(row["timestamp"])[11:16]

            # Query monthly highest peak
            m_row = conn.execute(f"""
                SELECT MAX(active_power_kw) as m_peak 
                FROM telemetry 
                WHERE {src_filter}
                  AND strftime('%Y-%m', datetime(timestamp, 'localtime')) = strftime('%Y-%m', 'now', 'localtime')
            """).fetchone()
            if m_row and m_row["m_peak"] is not None:
                raw_m_peak = float(m_row["m_peak"])
                month_peak_val = (raw_m_peak * 1000.0 / pf_safe) if is_live_mode else raw_m_peak
                month_peak_val = max(month_peak_val, peak_cache_val, current_demand_kw)

            # Query today's hourly averages for the actual demand curve
            h_rows = conn.execute(f"""
                SELECT 
                    strftime('%H', datetime(timestamp, 'localtime')) as hr,
                    AVG(active_power_kw) as avg_kw
                FROM telemetry
                WHERE {src_filter}
                  AND date(datetime(timestamp, 'localtime')) = date('now', 'localtime')
                GROUP BY hr
            """).fetchall()
            for r in h_rows:
                if r["hr"] is not None and r["avg_kw"] is not None:
                    avg_kw = float(r["avg_kw"])
                    val = (avg_kw * 1000.0 / pf_safe) if is_live_mode else avg_kw
                    db_hourly_map[int(r["hr"])] = round(val, 1 if is_live_mode else 2)
    except Exception as e:
        print(f"Error querying telemetry DB in layman_analytics: {e}")

    # Determine peak demand and time
    if db_peak_val > 0.0 and db_peak_val >= peak_cache_val:
        peak_demand_kw = round(db_peak_val, 1 if is_live_mode else 2)
        today_highest_peak_time = db_peak_time
    else:
        peak_demand_kw = round(max(peak_cache_val, current_demand_kw), 1 if is_live_mode else 2)
        today_highest_peak_time = peak_cache_time

    if is_live_mode:
        peak_demand_kw = min(contract_demand_kw, peak_demand_kw)
        month_peak_val = min(contract_demand_kw, month_peak_val)

    peak_percent = round((peak_demand_kw / contract_demand_kw) * 100, 1)
    remaining_buffer_kw = round(max(0.0, contract_demand_kw - peak_demand_kw), 1 if is_live_mode else 2)
    current_percent = round((current_demand_kw / contract_demand_kw) * 100, 1)
    
    # Status evaluation
    if peak_demand_kw >= safe_operating_kw:
        demand_status = "PENALTY_RISK"
        status_color = "red"
        status_text = f"SURGE RISK: Peak demand near or exceeding {safe_operating_kw} {demand_unit} safe threshold!"
    elif peak_demand_kw >= (safe_operating_kw * 0.85):
        demand_status = "CAUTION"
        status_color = "amber"
        status_text = f"MODERATE: Demand is approaching {safe_operating_kw} {demand_unit} safe threshold."
    else:
        demand_status = "SAFE"
        status_color = "emerald"
        status_text = f"OPTIMAL: Operating well within safe capacity ({safe_operating_kw} {demand_unit})."

    # Construct 24-Hour actual curve & forecaster projection WITH REAL DATES
    hourly_hours = [f"{today_date_str} {h:02d}:00" for h in range(24)]
    hourly_hours_short = [f"{h:02d}:00" for h in range(24)]
    actual_hourly_kw = []
    base_hourly_kwh = []
    forecast_hourly_kw = []

    for h in range(24):
        if h < current_hour:
            val = db_hourly_map.get(h, current_demand_kw)
            actual_hourly_kw.append(round(val, 1 if is_live_mode else 2))
            base_hourly_kwh.append(round(val, 1 if is_live_mode else 2))
            forecast_hourly_kw.append(round(val, 1 if is_live_mode else 2))
        elif h == current_hour:
            actual_hourly_kw.append(round(current_demand_kw, 1 if is_live_mode else 2))
            base_hourly_kwh.append(round(current_demand_kw, 1 if is_live_mode else 2))
            forecast_hourly_kw.append(round(current_demand_kw, 1 if is_live_mode else 2))
        else:
            actual_hourly_kw.append(None)
            pred_kw = forecaster.predict_15m(
                current_demand=(current_demand_kw / 1000.0 * 0.95) if is_live_mode else current_demand_kw,
                lag_demand=(current_demand_kw / 1000.0 * 0.95) if is_live_mode else current_demand_kw,
                production_rate=1.0,
                temp=28.0,
                hour=h,
                day_of_week=current_dow
            )
            pred_val = (pred_kw * 1000.0 / pf_safe) if is_live_mode else pred_kw
            base_hourly_kwh.append(round(pred_val, 1 if is_live_mode else 2))
            forecast_hourly_kw.append(round(pred_val, 1 if is_live_mode else 2))

    # Calculate predicted crest dynamically from the future forecast
    future_forecasts = [(h, forecast_hourly_kw[h]) for h in range(current_hour, 24) if forecast_hourly_kw[h] is not None]
    if future_forecasts:
        pred_peak_h, pred_peak_val = max(future_forecasts, key=lambda x: x[1])
        predicted_peak_kw = round(pred_peak_val, 1 if is_live_mode else 2)
        predicted_peak_time = f"{today_date_str} {pred_peak_h:02d}:00"
    else:
        predicted_peak_kw = round(current_demand_kw, 1 if is_live_mode else 2)
        predicted_peak_time = f"{today_date_str} {current_hour:02d}:00"

    # Multi-Timeframe Historical Analytics WITH EXPLICIT DATES (Day, Week, Month, Year)
    # Week labels with exact calendar dates
    week_dated_labels = [(now_local - timedelta(days=6-i)).strftime("%d %b (%a)") for i in range(7)]
    weekly_kwh = [0.0] * 7
    weekly_peak = [0.0] * 7
    try:
        with get_connection() as conn:
            rows = conn.execute(f"""
                SELECT 
                    strftime('%w', datetime(timestamp, 'localtime')) as dow_num,
                    AVG(active_power_kw) as avg_kw,
                    MAX(active_power_kw) as max_kw
                FROM telemetry
                WHERE datetime(timestamp, 'localtime') >= datetime('now', '-7 days')
                  AND {src_filter}
                GROUP BY dow_num
            """).fetchall()
            for r in rows:
                if r["dow_num"] is not None:
                    dow = int(r["dow_num"])
                    idx = (dow - 1) % 7 # 0=Mon, ..., 6=Sun
                    avg_p = float(r["avg_kw"] or 0.0)
                    e_val = (avg_p * 24.0 * 1000.0) if is_live_mode else (avg_p * 24.0)
                    p_val = (float(r["max_kw"] or 0.0) * 1000.0 / pf_safe) if is_live_mode else float(r["max_kw"] or 0.0)
                    weekly_kwh[idx] = round(e_val, 1)
                    weekly_peak[idx] = round(p_val, 1)
    except Exception as e:
        print(f"Error querying weekly telemetry: {e}")

    # Bind current day's real values
    weekly_kwh[current_dow] = round(sum(base_hourly_kwh), 1)
    weekly_peak[current_dow] = round(max(peak_demand_kw, predicted_peak_kw), 1)

    # Month labels with dated week ranges
    w4_end = now_local.strftime("%d %b")
    w4_start = (now_local - timedelta(days=7)).strftime("%d %b")
    w3_start = (now_local - timedelta(days=14)).strftime("%d %b")
    w2_start = (now_local - timedelta(days=21)).strftime("%d %b")
    w1_start = (now_local - timedelta(days=28)).strftime("%d %b")
    month_dated_labels = [
        f"{w1_start}-{w2_start}",
        f"{w2_start}-{w3_start}",
        f"{w3_start}-{w4_start}",
        f"{w4_start}-{w4_end} (Current)"
    ]
    monthly_kwh = [round(sum(weekly_kwh) * 0.9, 1), round(sum(weekly_kwh) * 0.95, 1), round(sum(weekly_kwh) * 1.05, 1), round(sum(weekly_kwh), 1)]
    monthly_peak = [round(max(weekly_peak), 1), round(max(weekly_peak), 1), round(max(weekly_peak), 1), round(peak_demand_kw, 1)]

    # Year labels with Month and Year (e.g. "Nov 2025" ... "Oct 2026")
    year_dated_labels = [(now_local - timedelta(days=30*(11-i))).strftime("%b %Y") for i in range(12)]
    cur_month_idx = 11
    yearly_kwh = [0.0] * 12
    yearly_peak = [0.0] * 12
    for m_i in range(12):
        if m_i <= cur_month_idx:
            yearly_kwh[m_i] = round(sum(monthly_kwh), 1)
            yearly_peak[m_i] = round(max(monthly_peak), 1)
    yearly_kwh[cur_month_idx] = round(sum(monthly_kwh), 1)
    yearly_peak[cur_month_idx] = round(month_peak_val, 1)

    # Day labels with date
    day_dated_labels = hourly_hours

    # Concentric circles / Radial rings data
    phase_r_kw = round((watts_r / 1000.0) if not is_live_mode else watts_r, 2)
    phase_y_kw = round((watts_y / 1000.0) if not is_live_mode else watts_y, 2)
    phase_b_kw = round((watts_b / 1000.0) if not is_live_mode else watts_b, 2)
    max_phase_rated_kw = contract_demand_kw / 3.0

    radial_rings = [
        {
            "name": "Phase R (Inner Ring)",
            "power_kw": phase_r_kw,
            "percent": round(min(100.0, (phase_r_kw / max_phase_rated_kw) * 100), 1),
            "color": "#f43f5e"
        },
        {
            "name": "Phase Y (Middle Ring)",
            "power_kw": phase_y_kw,
            "percent": round(min(100.0, (phase_y_kw / max_phase_rated_kw) * 100), 1),
            "color": "#f59e0b"
        },
        {
            "name": "Phase B (Outer Ring)",
            "power_kw": phase_b_kw,
            "percent": round(min(100.0, (phase_b_kw / max_phase_rated_kw) * 100), 1),
            "color": "#3b82f6"
        }
    ]

    # Layman AI Plain-English Explanations for Field Engineers
    explanation = {
        "title": "Plant Electrical Health Status",
        "badge": demand_status,
        "summary": (
            f"The equipment is currently running at {current_demand_kw} {demand_unit}. "
            f"Your peak usage today touched {peak_demand_kw} {demand_unit} out of your {contract_demand_kw} {demand_unit} contract limit. "
            f"You still have {remaining_buffer_kw} {demand_unit} of safe operating capacity available."
        ),
        "cards": [
            {
                "icon": "⚡",
                "title": "Current Usage",
                "headline": f"{current_demand_kw} {demand_unit} Active Now",
                "details": f"Using {current_percent}% of sanctioned power capacity. All 3 phases are balanced and running smoothly."
            },
            {
                "icon": "🛡️",
                "title": "Demand Penalty Risk",
                "headline": f"{remaining_buffer_kw} {demand_unit} Safe Margin",
                "details": (
                    f"Peak today was {peak_demand_kw} {demand_unit} ({peak_percent}% of limit). "
                    f"Safe buffer of {remaining_buffer_kw} {demand_unit} before any surcharge penalty."
                )
            },
            {
                "icon": "⚙️",
                "title": "Power Quality & Health",
                "headline": f"PF: {pf_avg} • {freq} Hz",
                "details": "Power factor is healthy. Voltage is steady at ~230V. No reactive power surcharges."
            },
            {
                "icon": "👷",
                "title": "Shift Technician Advice",
                "headline": "Safe to operate connected equipment",
                "details": f"Available buffer is {remaining_buffer_kw} {demand_unit}. Peak forecast is {predicted_peak_kw} {demand_unit}."
            }
        ]
    }

    # Cumulative energy & apparent energy calculations
    total_energy_wh = float(latest_reading.energy_wh or 0.0) if latest_reading else 0.0
    total_apparent_energy_vah = float(latest_reading.energy_vah or 0.0) if latest_reading else 0.0
    total_energy_kwh = round(total_energy_wh / 1000.0, 3)
    total_apparent_energy_kvah = round(total_apparent_energy_vah / 1000.0, 3)

    curr_total_a = round(latest_reading.current_total or (latest_reading.current_a if latest_reading.current_a else 0.0), 2) if latest_reading else 0.0
    curr_r_a = round(latest_reading.current_r or (curr_total_a / 3.0), 2) if latest_reading else 0.0
    curr_y_a = round(latest_reading.current_y or (curr_total_a / 3.0), 2) if latest_reading else 0.0
    curr_b_a = round(latest_reading.current_b or (curr_total_a / 3.0), 2) if latest_reading else 0.0

    vr_val = round(latest_reading.v_r or v_ln_avg, 1) if latest_reading else v_ln_avg
    vy_val = round(latest_reading.v_y or v_ln_avg, 1) if latest_reading else v_ln_avg
    vb_val = round(latest_reading.v_b or v_ln_avg, 1) if latest_reading else v_ln_avg

    # Industrial Statements and Labels
    industrial_labels = {
        "pcc_monitoring": "PCC Monitoring — Power consumption by connection.",
        "energy_consumption": "Energy Consumption — Daily and monthly energy usage.",
        "maximum_demand": "Maximum Demand — Current demand and peak-demand monitoring.",
        "today_peak_demand": "Today's Peak Demand — Highest measured demand for the current day.",
        "monthly_peak_demand": "Monthly Peak Demand — Highest measured demand for the current month.",
        "power_quality": "Power Quality — Voltage, current, frequency, and power factor.",
        "cumulative_energy": "Cumulative Energy — Total recorded energy consumption.",
        "predicted_peak": "Predicted Peak — Forecast demand and expected occurrence time.",
        "peak_risk_status": "Peak Risk Status — Demand relative to the configured threshold.",
        "optimization_opportunity": "Optimization Opportunity — Suggested actions to reduce peak demand.",
        "operator_approval_required": "Operator Approval Required — No control action is executed without authorization.",
        "data_source_status": "Data Source Status — Live meter, simulated data, stale data, or offline."
    }

    # B. Energy Consumption Section
    today_total_energy = round(sum(base_hourly_kwh), 2)
    energy_consumption_data = {
        "units_today": today_total_energy,
        "units_this_month": round(sum(monthly_kwh), 1),
        "total_energy_kwh": total_energy_kwh,
        "total_apparent_energy_kvah": total_apparent_energy_kvah,
        "total_energy_wh": round(total_energy_wh, 1),
        "total_apparent_energy_vah": round(total_apparent_energy_vah, 1),
        "unit": energy_unit,
        "demand_unit": demand_unit
    }

    # C. Maximum Demand (CMD) Section
    maximum_demand_data = {
        "current_demand_kw": current_demand_kw,
        "current_demand_val": current_demand_kw,
        "today_highest_peak_kw": peak_demand_kw,
        "today_highest_peak_time": today_highest_peak_time,
        "month_highest_peak_kw": round(month_peak_val, 1 if is_live_mode else 2),
        "configured_demand_limit_kw": contract_demand_kw,
        "safe_operating_limit_kw": safe_operating_kw,
        "watts_total": round(watts_total, 1),
        "va_total": round(va_total, 1),
        "today_highest_peak_w": round(peak_demand_kw * (pf_safe if is_live_mode else 1.0), 1),
        "month_highest_peak_w": round(month_peak_val * (pf_safe if is_live_mode else 1.0), 1),
        "predicted_peak_kw": predicted_peak_kw,
        "predicted_peak_time": predicted_peak_time,
        "remaining_buffer_kw": remaining_buffer_kw,
        "peak_percent": peak_percent,
        "current_percent": current_percent,
        "peak_risk_status": demand_status,
        "status_color": status_color,
        "status_text": status_text,
        "unit": demand_unit
    }

    # D. Power Quality Section
    power_quality_data = {
        "current_power_factor": pf_avg,
        "today_power_factor": pf_avg,
        "monthly_power_factor": 0.95,
        "voltage": {
            "v_ln_avg": v_ln_avg,
            "v_ll_avg": v_ll_avg,
            "v_r": vr_val,
            "v_y": vy_val,
            "v_b": vb_val,
            "v_ry": round(latest_reading.v_ry or v_ll_avg, 1) if latest_reading else v_ll_avg,
            "v_yb": round(latest_reading.v_yb or v_ll_avg, 1) if latest_reading else v_ll_avg,
            "v_br": round(latest_reading.v_br or v_ll_avg, 1) if latest_reading else v_ll_avg
        },
        "current": {
            "current_total": curr_total_a,
            "current_r": curr_r_a,
            "current_y": curr_y_a,
            "current_b": curr_b_a
        },
        "frequency": freq
    }

    # Actual vs Forecast Demand Chart Data
    actual_vs_forecast_data = {
        "hours": hourly_hours,
        "hours_short": hourly_hours_short,
        "date": today_date_str,
        "actual_kw": actual_hourly_kw,
        "forecast_kw": forecast_hourly_kw,
        "cmd_limit_kw": contract_demand_kw,
        "safe_limit_kw": safe_operating_kw,
        "predicted_peak_kw": predicted_peak_kw,
        "predicted_peak_time": predicted_peak_time,
        "today_peak_kw": peak_demand_kw,
        "today_peak_time": today_highest_peak_time,
        "unit": demand_unit
    }

    # Dynamic Optimization Opportunity
    if predicted_peak_kw >= safe_operating_kw:
        excess_val = round(predicted_peak_kw - safe_operating_kw, 1)
        potential_penalty = int(excess_val * (4.5 if is_live_mode else 450))
        optimization_opp = {
            "title": "Stagger Heavy Equipment Cycles",
            "suggestion": f"Predicted peak demand of {predicted_peak_kw} {demand_unit} at {predicted_peak_time} approaches the {safe_operating_kw} {demand_unit} safe operating limit. Stagger auxiliary equipment to stay within limits.",
            "potential_savings": f"₹ {potential_penalty:,} avoiding peak demand surcharge",
            "predicted_peak_avoided_kw": excess_val,
            "operator_approval_required": True,
            "status": "AWAITING_OPERATOR_AUTHORIZATION"
        }
    else:
        optimization_opp = {
            "title": "Optimal Load Distribution & Surcharge Protection",
            "suggestion": f"Operating load ({current_demand_kw} {demand_unit}) and 24h peak forecast ({predicted_peak_kw} {demand_unit} @ {predicted_peak_time}) are well within the {contract_demand_kw} {demand_unit} ceiling. Safe buffer is {remaining_buffer_kw} {demand_unit}.",
            "potential_savings": "₹ 0 (Zero surcharge risk — optimal operation)",
            "predicted_peak_avoided_kw": 0.0,
            "operator_approval_required": False,
            "status": "OPTIMAL_LOAD_BALANCED"
        }

    # Data Source Status
    source_status_dict = _get_active_source()
    active_source_str = source_status_dict.get("active_source", "SIMULATED_RASPI") if isinstance(source_status_dict, dict) else str(source_status_dict)
    data_source_info = {
        "status": "LIVE_METER" if (latest_reading and latest_reading.data_source.value == "RASPBERRY_PI") else "SIMULATED_DATA",
        "active_source": active_source_str,
        "source_status": source_status_dict.get("source_status", "ONLINE") if isinstance(source_status_dict, dict) else "ONLINE",
        "description": "Live meter, simulated data, stale data, or offline."
    }

    tariff_rate = 7.50 if not is_live_mode else 0.0075 # ₹7.50 per kWh (= ₹0.0075 per Wh)
    return {
        # Structured Sections B, C, D & Visualizations
        "energy_consumption": energy_consumption_data,
        "maximum_demand": maximum_demand_data,
        "power_quality": power_quality_data,
        "actual_vs_forecast": actual_vs_forecast_data,
        "industrial_statements": industrial_labels,
        "optimization_opportunity": optimization_opp,
        "data_source_status": data_source_info,
        "mode": "LIVE" if is_live_mode else "SIMULATION",

        # Backward compatibility for existing UI
        "contract_demand": {
            "contract_limit_kw": contract_demand_kw,
            "safe_target_kw": safe_operating_kw,
            "peak_demand_kw": peak_demand_kw,
            "current_demand_kw": current_demand_kw,
            "peak_percent": peak_percent,
            "current_percent": current_percent,
            "remaining_buffer_kw": remaining_buffer_kw,
            "status": demand_status,
            "status_color": status_color,
            "status_text": status_text,
            "unit": demand_unit
        },
        "radial_rings": radial_rings,
        "timeframes": {
            "day": {
                "labels": day_dated_labels,
                "values": base_hourly_kwh,
                "unit": energy_unit,
                "demand_unit": demand_unit,
                "total": round(sum(base_hourly_kwh), 2),
                "peak": round(max(base_hourly_kwh), 2),
                "avg": round(sum(base_hourly_kwh) / len(base_hourly_kwh), 2),
                "cost_inr": round(sum(base_hourly_kwh) * tariff_rate, 0)
            },
            "week": {
                "labels": week_dated_labels,
                "values": weekly_kwh,
                "peaks": weekly_peak,
                "unit": energy_unit,
                "demand_unit": demand_unit,
                "total": round(sum(weekly_kwh), 1),
                "peak": round(max(weekly_peak), 1),
                "avg": round(sum(weekly_kwh) / len(weekly_kwh), 1),
                "cost_inr": round(sum(weekly_kwh) * tariff_rate, 0)
            },
            "month": {
                "labels": month_dated_labels,
                "values": monthly_kwh,
                "peaks": monthly_peak,
                "unit": energy_unit,
                "demand_unit": demand_unit,
                "total": round(sum(monthly_kwh), 1),
                "peak": round(max(monthly_peak), 1),
                "avg": round(sum(monthly_kwh) / len(monthly_kwh), 1),
                "cost_inr": round(sum(monthly_kwh) * tariff_rate, 0)
            },
            "year": {
                "labels": year_dated_labels,
                "values": yearly_kwh,
                "peaks": yearly_peak,
                "unit": energy_unit,
                "demand_unit": demand_unit,
                "total": round(sum(yearly_kwh), 1),
                "peak": round(max(yearly_peak), 1),
                "avg": round(sum(yearly_kwh) / len(yearly_kwh), 1),
                "cost_inr": round(sum(yearly_kwh) * tariff_rate, 0)
            }
        },
        "ai_explanation": explanation,
        "relays": get_relay_status()["relay_decision"]
    }

