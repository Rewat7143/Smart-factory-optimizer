from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone

router = APIRouter()

# In-memory stores
active_events = {}
command_history = []

class ApprovalPayload(BaseModel):
    event_id: str
    action: str # "APPROVE" or "REJECT"
    asset_id: str
    
@router.get("/control/events")
def get_control_events():
    # Return all active events
    events = []
    now = datetime.now(timezone.utc)
    for event_id, event in list(active_events.items()):
        # Expiry check
        if event["status"] in ["AWAITING_APPROVAL"] and (now - event["created_at"]).total_seconds() > 300:
            event["status"] = "EXPIRED"
            
        events.append({
            "event_id": event_id,
            "type": event["type"],
            "severity": event["severity"],
            "message": event["message"],
            "status": event["status"],
            "asset_id": event.get("asset_id"),
            "proposed_action": event.get("proposed_action"),
            "impact_kw": event.get("impact_kw"),
            "created_at": event["created_at"].isoformat(),
            "acknowledged": event.get("acknowledged", False)
        })
        
    # Sort by created_at desc
    events.sort(key=lambda x: x["created_at"], reverse=True)
    return {"events": events}

@router.post("/control/acknowledge")
def acknowledge_event(payload: dict):
    event_id = payload.get("event_id")
    if event_id in active_events:
        active_events[event_id]["acknowledged"] = True
        return {"status": "SUCCESS"}
    raise HTTPException(status_code=404, detail="Event not found")

@router.post("/control/approve")
def approve_command(payload: ApprovalPayload):
    event_id = payload.event_id
    if event_id not in active_events:
        raise HTTPException(status_code=404, detail="Command not found or expired")
        
    event = active_events[event_id]
    if event["status"] != "AWAITING_APPROVAL":
        raise HTTPException(status_code=400, detail=f"Cannot approve command in state {event['status']}")
        
    if payload.action == "APPROVE":
        event["status"] = "SENT"
        # Simulate hardware gateway transmission delay then set to ACKNOWLEDGED or VERIFIED
        # In a real system, a background worker handles this.
        # We will just record it in command history.
        command_history.append({
            "command_id": event_id,
            "asset_id": payload.asset_id,
            "action": event["proposed_action"],
            "status": "SENT",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        return {"status": "SENT", "message": "Command approved and sent to hardware gateway."}
        
    elif payload.action == "REJECT":
        event["status"] = "REJECTED"
        return {"status": "REJECTED", "message": "Command rejected by operator."}
        
    raise HTTPException(status_code=400, detail="Invalid action")

def register_peak_event(peak_type: str, demand: float, limit: float, actions: list):
    """Called by backend loops when a peak is detected."""
    now = datetime.now(timezone.utc)
    
    # Cooldown check: don't create duplicate events within 5 minutes
    for eid, ev in active_events.items():
        if ev["type"] == peak_type and ev["status"] in ["AWAITING_APPROVAL", "SENT"] and (now - ev["created_at"]).total_seconds() < 300:
            return # Duplicate
            
    event_id = f"EVT-{int(now.timestamp())}"
    
    # Determine top action
    proposed_action = None
    asset_id = None
    impact = 0.0
    if actions:
        top = actions[0]
        proposed_action = top.get("action")
        asset_id = top.get("asset_id")
        impact = top.get("reduction_kw", 0.0)
        
    active_events[event_id] = {
        "type": peak_type, # MEASURED_PEAK or PREDICTED_PEAK
        "severity": "CRITICAL" if peak_type == "MEASURED_PEAK" else "WARNING",
        "message": f"Demand at {demand:.1f} kW exceeds limit of {limit:.1f} kW." if peak_type == "MEASURED_PEAK" else f"Predicted demand {demand:.1f} kW will exceed limit of {limit:.1f} kW.",
        "status": "AWAITING_APPROVAL" if actions else "NO_ACTION_AVAILABLE",
        "asset_id": asset_id,
        "proposed_action": proposed_action,
        "impact_kw": impact,
        "created_at": now,
        "acknowledged": False
    }

@router.post("/control/dispatch-action")
def dispatch_action(payload: dict):
    asset_id = payload.get("asset_id", "HVAC-001")
    action_text = payload.get("action", "Modulate load")
    now_iso = datetime.now(timezone.utc).isoformat()
    cmd_id = f"CMD-{int(datetime.now(timezone.utc).timestamp())}"
    command_history.append({
        "command_id": cmd_id,
        "asset_id": asset_id,
        "action": action_text,
        "status": "SENT",
        "timestamp": now_iso
    })
    return {
        "status": "SUCCESS",
        "command_id": cmd_id,
        "message": f"Optimization dispatch command transmitted to Modbus RTU controller for {asset_id}.",
        "timestamp": now_iso
    }


