import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timezone, timedelta
from api.control import active_events, command_history, register_peak_event

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_control_state():
    active_events.clear()
    command_history.clear()
    yield

def test_control_approval_lifecycle():
    # 1. Register a peak event (creates AWAITING_APPROVAL)
    register_peak_event("MEASURED_PEAK", 110.0, 100.0, [{"action": "Turn off HVAC", "asset_id": "HVAC-1", "reduction_kw": 20.0}])
    
    # Verify no duplicate events are created immediately (cooldown check)
    register_peak_event("MEASURED_PEAK", 115.0, 100.0, [{"action": "Turn off HVAC", "asset_id": "HVAC-1", "reduction_kw": 20.0}])
    assert len(active_events) == 1, "Duplicate peak events should be blocked by cooldown"
    
    event_id = list(active_events.keys())[0]
    
    # 2. Get events via API
    res = client.get("/api/control/events")
    assert res.status_code == 200
    data = res.json()["events"]
    assert len(data) == 1
    assert data[0]["status"] == "AWAITING_APPROVAL", "Command MUST NOT emit before approval"
    assert data[0]["proposed_action"] == "Turn off HVAC"
    
    # 3. Reject a command
    rej_res = client.post("/api/control/approve", json={"event_id": event_id, "action": "REJECT", "asset_id": "HVAC-1"})
    assert rej_res.status_code == 200
    assert rej_res.json()["status"] == "REJECTED"
    
    # 4. Try to approve a rejected command (Invalid)
    inv_res = client.post("/api/control/approve", json={"event_id": event_id, "action": "APPROVE", "asset_id": "HVAC-1"})
    assert inv_res.status_code == 400
    assert "Cannot approve command in state" in inv_res.json()["detail"]
    
def test_control_expiry():
    # Simulate an expired event
    event_id = "EVT-TEST-EXPIRE"
    active_events[event_id] = {
        "type": "PREDICTED_PEAK",
        "severity": "WARNING",
        "message": "Predicted demand 110.0 kW.",
        "status": "AWAITING_APPROVAL",
        "asset_id": "CHLR-1",
        "proposed_action": "Reduce Chiller Load",
        "impact_kw": 15.0,
        "created_at": datetime.now(timezone.utc) - timedelta(seconds=400),
        "acknowledged": False
    }
    
    # 1. Fetching events should automatically flag it as EXPIRED
    res = client.get("/api/control/events")
    data = res.json()["events"]
    assert data[0]["status"] == "EXPIRED"
    
    # 2. Approving an expired event fails
    exp_res = client.post("/api/control/approve", json={"event_id": event_id, "action": "APPROVE", "asset_id": "CHLR-1"})
    assert exp_res.status_code == 400
    assert "Cannot approve" in exp_res.json()["detail"]
