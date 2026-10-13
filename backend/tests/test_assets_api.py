import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_initial_three_assets_exist(client):
    r = client.get("/api/assets")
    assert r.status_code == 200
    data = r.json()
    ids = [a["asset_id"] for a in data["assets"]]
    assert "LOAD-001" in ids
    assert "LOAD-002" in ids
    assert "LOAD-003" in ids

def test_load_001_is_mandatory_and_protected(client):
    r = client.get("/api/assets/LOAD-001")
    assert r.status_code == 200
    asset = r.json()["asset"]
    assert asset["load_classification"] == "Mandatory"
    assert asset["is_protected"] == 1
    # Check that permitted actions do not include switch-off
    assert "authorized_switch_off" not in asset["permitted_actions"]

def test_immutable_asset_id_and_creation(client):
    r = client.post("/api/assets", json={
        "name": "Line 2 Hydraulic Unit",
        "equipment_type": "Hydraulic Power Pack",
        "rated_capacity_kw": 25.0,
        "load_classification": "Flexible",
        "priority_order": 2,
        "permitted_actions": ["monitor_only", "delay_startup"]
    })
    assert r.status_code == 201
    created = r.json()["asset"]
    new_id = created["asset_id"]
    assert new_id.startswith("LOAD-")

    # Try updating with asset_id in payload - should not change ID
    update_r = client.put(f"/api/assets/{new_id}", json={
        "asset_id": "TAMPER-ID-01",
        "name": "Line 2 Hydraulic Unit Updated"
    })
    assert update_r.status_code == 200
    updated = update_r.json()["asset"]
    assert updated["asset_id"] == new_id
    assert updated["name"] == "Line 2 Hydraulic Unit Updated"

def test_protected_safety_rule_enforced(client):
    # Attempting to create a Mandatory load with authorized_switch_off must fail
    r = client.post("/api/assets", json={
        "name": "Critical Melt Furnace",
        "load_classification": "Mandatory",
        "is_protected": True,
        "permitted_actions": ["authorized_switch_off"]
    })
    assert r.status_code == 400
    assert "Safety violation" in r.json()["detail"]

def test_archive_and_unarchive_flow(client):
    # Create asset
    create_r = client.post("/api/assets", json={
        "name": "Temporary Test Pump",
        "load_classification": "Opportunistic"
    })
    asset_id = create_r.json()["asset"]["asset_id"]

    # Archive
    arc_r = client.post(f"/api/assets/{asset_id}/archive")
    assert arc_r.status_code == 200
    assert arc_r.json()["asset"]["is_archived"] == 1

    # Check that default listing excludes archived
    list_r = client.get("/api/assets")
    active_ids = [a["asset_id"] for a in list_r.json()["assets"]]
    assert asset_id not in active_ids

    # Check listing with include_archived=True includes it
    list_all_r = client.get("/api/assets?include_archived=true")
    all_ids = [a["asset_id"] for a in list_all_r.json()["assets"]]
    assert asset_id in all_ids

    # Unarchive
    unarc_r = client.post(f"/api/assets/{asset_id}/unarchive")
    assert unarc_r.status_code == 200
    assert unarc_r.json()["asset"]["is_archived"] == 0

def test_control_approval_and_rejection_audit(client):
    # Create a recommendation on LOAD-002
    from database import db
    db.create_control_action_record({
        "action_id": "REC-TEST-AUDIT-01",
        "asset_id": "LOAD-002",
        "action_type": "delay_startup",
        "recommendation_reason": "Test peak delay",
        "current_demand_kw": 92.0,
        "threshold_kw": 90.0,
        "expected_impact_kw": 6.0
    })

    # Approve
    app_r = client.post("/api/assets/LOAD-002/control/decide", json={
        "action_id": "REC-TEST-AUDIT-01",
        "decision": "APPROVE",
        "operator_id": "OP-SHIFT-SUPERVISOR",
        "operator_notes": "Approved for 15 minute delay"
    })
    assert app_r.status_code == 200
    audit = app_r.json()["audit_record"]
    assert audit["status"] == "APPROVED"
    assert audit["operator_id"] == "OP-SHIFT-SUPERVISOR"
    assert audit["decided_at"] is not None

def test_nonexistent_asset_404(client):
    r = client.get("/api/assets/DOES-NOT-EXIST-999")
    assert r.status_code == 404
