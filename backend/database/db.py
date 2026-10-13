import sqlite3
import os
import uuid
from typing import List, Dict, Any, Optional

# Ensure database directory exists
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("DATABASE_URL", os.path.join(DB_DIR, "telemetry.db")).replace("sqlite:///", "")

# All 27 parameter columns from L&T WL4400 memory map (addresses 40101 - 40217)
MEMORY_MAP_COLUMNS = [
    ("watts_total", "REAL"),
    ("watts_r", "REAL"),
    ("watts_y", "REAL"),
    ("watts_b", "REAL"),
    ("pf_avg", "REAL"),
    ("pf_r", "REAL"),
    ("pf_y", "REAL"),
    ("pf_b", "REAL"),
    ("va_total", "REAL"),
    ("va_r", "REAL"),
    ("va_y", "REAL"),
    ("va_b", "REAL"),
    ("v_ll_avg", "REAL"),
    ("v_ry", "REAL"),
    ("v_yb", "REAL"),
    ("v_br", "REAL"),
    ("v_ln_avg", "REAL"),
    ("v_r", "REAL"),
    ("v_y", "REAL"),
    ("v_b", "REAL"),
    ("current_total", "REAL"),
    ("current_r", "REAL"),
    ("current_y", "REAL"),
    ("current_b", "REAL"),
    ("frequency", "REAL"),
    ("energy_wh", "REAL"),
    ("energy_vah", "REAL"),
    ("load_hours", "INTEGER"),
]

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                record_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                factory_id TEXT,
                asset_id TEXT,
                voltage_v REAL,
                current_a REAL,
                active_power_kw REAL,
                energy_kwh REAL,
                frequency_hz REAL,
                power_factor REAL,
                machine_state TEXT,
                data_source TEXT,
                data_quality TEXT,
                watts_total REAL,
                watts_r REAL,
                watts_y REAL,
                watts_b REAL,
                pf_avg REAL,
                pf_r REAL,
                pf_y REAL,
                pf_b REAL,
                va_total REAL,
                va_r REAL,
                va_y REAL,
                va_b REAL,
                v_ll_avg REAL,
                v_ry REAL,
                v_yb REAL,
                v_br REAL,
                v_ln_avg REAL,
                v_r REAL,
                v_y REAL,
                v_b REAL,
                current_total REAL,
                current_r REAL,
                current_y REAL,
                current_b REAL,
                frequency REAL,
                energy_wh REAL,
                energy_vah REAL,
                load_hours INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Safe migration for existing SQLite databases
        cursor = conn.execute("PRAGMA table_info(telemetry)")
        existing_cols = {row["name"] for row in cursor.fetchall()}
        
        for col_name, col_type in MEMORY_MAP_COLUMNS:
            if col_name not in existing_cols:
                try:
                    conn.execute(f"ALTER TABLE telemetry ADD COLUMN {col_name} {col_type}")
                except Exception as e:
                    print(f"Column migration notice for {col_name}: {e}")
                    
        conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_source ON telemetry(data_source)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_asset ON telemetry(asset_id)")
        
        # Assets Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                asset_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                equipment_type TEXT DEFAULT 'Not configured',
                manufacturer_model TEXT DEFAULT 'Not configured',
                location TEXT DEFAULT 'Not configured',
                rated_capacity_kw REAL,
                rated_voltage_v REAL,
                phase_config TEXT DEFAULT 'Not configured',
                pcc_association TEXT DEFAULT 'PCC-01',
                meter_association TEXT DEFAULT 'RPi-METER-01',
                load_classification TEXT DEFAULT 'Flexible',
                priority_order INTEGER DEFAULT 2,
                is_protected INTEGER DEFAULT 0,
                permitted_actions TEXT DEFAULT '["monitor_only"]',
                min_runtime_minutes INTEGER DEFAULT 15,
                min_offtime_minutes INTEGER DEFAULT 15,
                restart_delay_minutes INTEGER DEFAULT 5,
                operating_schedule TEXT DEFAULT '24/7 Continuous',
                production_constraints TEXT DEFAULT 'Not configured',
                operator_notes TEXT DEFAULT 'Not configured',
                maintenance_notes TEXT DEFAULT 'Not configured',
                is_archived INTEGER DEFAULT 0,
                archived_at TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_archived ON assets(is_archived)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_classification ON assets(load_classification)")

        # Asset Control Actions & Audit Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS asset_control_audit (
                action_id TEXT PRIMARY KEY,
                asset_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                recommendation_reason TEXT,
                current_demand_kw REAL,
                threshold_kw REAL,
                expected_impact_kw REAL,
                production_implications TEXT,
                status TEXT DEFAULT 'AWAITING_APPROVAL',
                operator_id TEXT,
                operator_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                decided_at TEXT,
                executed_at TEXT,
                verified_at TEXT,
                physical_verification_status TEXT DEFAULT 'PENDING'
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_asset ON asset_control_audit(asset_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_status ON asset_control_audit(status)")

        # Seed initial assets if empty
        cursor = conn.execute("SELECT COUNT(*) FROM assets")
        if cursor.fetchone()[0] == 0:
            initial_assets = [
                # Mandatory & Protected Load
                (
                    "LOAD-001", "LOAD-001", "Not configured", "Not configured", "Not configured",
                    None, None, "Not configured", "PCC-01", "RPi-METER-01",
                    "Mandatory", 1, 1, '["monitor_only"]',
                    30, 30, 10, "24/7 Continuous",
                    "Mandatory base load — protected from peak shedding under plant safety policy.",
                    "Critical asset. Shedding and automated switch-off strictly forbidden.",
                    "Not configured", 0, None
                ),
                # Flexible / Second shedding candidate
                (
                    "LOAD-002", "LOAD-002", "Not configured", "Not configured", "Not configured",
                    None, None, "Not configured", "PCC-01", "RPi-METER-01",
                    "Flexible", 2, 0, '["monitor_only", "delay_startup", "modulate_setpoint"]',
                    15, 15, 5, "Flexible Shift Hours",
                    "Flexible process load — second shedding candidate.",
                    "Tolerates up to 15-minute start delay if factory demand approaches contract ceiling.",
                    "Not configured", 0, None
                ),
                # Flexible / First shedding candidate
                (
                    "LOAD-003", "LOAD-003", "Not configured", "Not configured", "Not configured",
                    None, None, "Not configured", "PCC-01", "RPi-METER-01",
                    "Flexible", 3, 0, '["monitor_only", "delay_startup", "authorized_switch_off"]',
                    10, 20, 5, "Intermittent / Auxiliary",
                    "Flexible load — first shedding candidate during peak demand alerts.",
                    "Primary candidate for rapid peak demand curtailment.",
                    "Not configured", 0, None
                ),
                # Factory Motors & Utility loads for seamless digital twin / energy integration
                (
                    "M-001", "Production Motor 01", "Induction Motor", "Siemens 1LE1", "Shop Floor 1",
                    15.0, 415.0, "3-Phase 415V", "PCC-01", "RPi-METER-01",
                    "Mandatory", 1, 1, '["monitor_only"]',
                    20, 10, 5, "24/7 Continuous",
                    "Primary line drive — Protected from shedding.",
                    "Main production motor for Section A.",
                    "Scheduled quarterly bearing greasing in 45 days.", 0, None
                ),
                (
                    "M-002", "Production Motor 02", "Induction Motor", "Siemens 1LE1", "Shop Floor 1",
                    18.0, 415.0, "3-Phase 415V", "PCC-01", "RPi-METER-01",
                    "Mandatory", 1, 1, '["monitor_only"]',
                    20, 10, 5, "24/7 Continuous",
                    "Heavy extruder drive — Protected from shedding.",
                    "Secondary production motor for Section B.",
                    "Healthy insulation resistance (12.4 MΩ).", 0, None
                ),
                (
                    "M-003", "Production Motor 03", "Induction Motor", "ABB M3BP", "Shop Floor 2",
                    10.0, 415.0, "3-Phase 415V", "PCC-01", "RPi-METER-01",
                    "Mandatory", 1, 1, '["monitor_only"]',
                    15, 15, 5, "Two Shifts (06:00 - 22:00)",
                    "Conveyor transfer drive — Protected from shedding.",
                    "Section C packaging line.",
                    "Belt tension checked weekly.", 0, None
                ),
                (
                    "CMP-001", "Air Compressor", "Rotary Screw Compressor", "Atlas Copco GA 30", "Utility Bay",
                    30.0, 415.0, "3-Phase 415V", "PCC-01", "RPi-METER-01",
                    "Flexible", 2, 0, '["monitor_only", "delay_startup", "modulate_setpoint"]',
                    15, 20, 10, "24/7 Continuous",
                    "Pneumatic air supply for plant tools. Unloader can idle for up to 12 minutes.",
                    "Air receiver tank maintains 7.2 bar buffer pressure.",
                    "Oil filter replaced 14 days ago.", 0, None
                ),
                (
                    "HVAC-001", "HVAC Chiller System", "Centrifugal Chiller", "Carrier 30XA", "Rooftop Plant",
                    20.0, 415.0, "3-Phase 415V", "PCC-01", "RPi-METER-01",
                    "Opportunistic", 3, 0, '["monitor_only", "delay_startup", "modulate_setpoint", "authorized_switch_off"]',
                    30, 15, 10, "Day Shift (08:00 - 18:00)",
                    "Thermal inertia allows 20-minute compressor pause without ambient breach.",
                    "Comfort cooling for administrative and assembly bays.",
                    "Seasonal refrigerant charge checked.", 0, None
                ),
                (
                    "AUX-001", "Auxiliary Facility Load", "Auxiliary Equipment", "Generic Industrial", "Utility Room",
                    5.0, 230.0, "1-Phase 230V", "PCC-01", "RPi-METER-01",
                    "Opportunistic", 4, 0, '["monitor_only", "authorized_switch_off"]',
                    5, 5, 2, "Intermittent",
                    "Non-production auxiliary load; deferrable at will.",
                    "Auxiliary lighting and support circulation fans.",
                    "No critical maintenance required.", 0, None
                )
            ]
            conn.executemany("""
                INSERT INTO assets (
                    asset_id, name, equipment_type, manufacturer_model, location,
                    rated_capacity_kw, rated_voltage_v, phase_config, pcc_association, meter_association,
                    load_classification, priority_order, is_protected, permitted_actions,
                    min_runtime_minutes, min_offtime_minutes, restart_delay_minutes, operating_schedule,
                    production_constraints, operator_notes, maintenance_notes, is_archived, archived_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, initial_assets)

            # Seed an initial pending recommendation for LOAD-003 to demonstrate the approval workflow
            initial_audit = [
                (
                    "REC-LOAD003-01", "LOAD-003", "delay_startup",
                    "Demand forecast predicts factory active power approaching 90 kW CMD ceiling within next 15 minutes. Deferring startup preserves operating headroom.",
                    91.0, 90.0, 8.5,
                    "Flexible auxiliary load can be deferred by up to 20 minutes with zero impact on main production line.",
                    "AWAITING_APPROVAL", None, None, None, None, None, "PENDING"
                ),
                (
                    "REC-CMP001-01", "CMP-001", "modulate_setpoint",
                    "Trim receiver pressure setpoint by 0.5 bar during peak tariff window to shave 3.2 kW.",
                    91.0, 90.0, 3.2,
                    "Accumulator buffer maintains tools within compliant 6.8 - 7.5 bar operating range.",
                    "AWAITING_APPROVAL", None, None, None, None, None, "PENDING"
                )
            ]
            conn.executemany("""
                INSERT INTO asset_control_audit (
                    action_id, asset_id, action_type, recommendation_reason,
                    current_demand_kw, threshold_kw, expected_impact_kw, production_implications,
                    status, operator_id, operator_notes, decided_at, executed_at, verified_at,
                    physical_verification_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, initial_audit)

        conn.commit()

def insert_telemetry(record: dict) -> bool:
    try:
        # Cross-populate standard & memory map aliases if missing
        active_power_kw = record.get('active_power_kw')
        watts_total = record.get('watts_total')
        if active_power_kw is None and watts_total is not None:
            active_power_kw = watts_total / 1000.0
        elif watts_total is None and active_power_kw is not None:
            watts_total = active_power_kw * 1000.0

        energy_kwh = record.get('energy_kwh')
        energy_wh = record.get('energy_wh')
        if energy_kwh is None and energy_wh is not None:
            energy_kwh = energy_wh / 1000.0
        elif energy_wh is None and energy_kwh is not None:
            energy_wh = energy_kwh * 1000.0

        voltage_v = record.get('voltage_v')
        v_ln_avg = record.get('v_ln_avg')
        if voltage_v is None and v_ln_avg is not None:
            voltage_v = v_ln_avg
        elif v_ln_avg is None and voltage_v is not None:
            v_ln_avg = voltage_v

        current_a = record.get('current_a')
        current_total = record.get('current_total')
        if current_a is None and current_total is not None:
            current_a = current_total
        elif current_total is None and current_a is not None:
            current_total = current_a

        frequency_hz = record.get('frequency_hz')
        frequency = record.get('frequency')
        if frequency_hz is None and frequency is not None:
            frequency_hz = frequency
        elif frequency is None and frequency_hz is not None:
            frequency = frequency_hz

        power_factor = record.get('power_factor')
        pf_avg = record.get('pf_avg')
        if power_factor is None and pf_avg is not None:
            power_factor = pf_avg
        elif pf_avg is None and power_factor is not None:
            pf_avg = power_factor

        cols = [
            "record_id", "timestamp", "factory_id", "asset_id",
            "voltage_v", "current_a", "active_power_kw", "energy_kwh",
            "frequency_hz", "power_factor", "machine_state", "data_source", "data_quality",
            "watts_total", "watts_r", "watts_y", "watts_b",
            "pf_avg", "pf_r", "pf_y", "pf_b",
            "va_total", "va_r", "va_y", "va_b",
            "v_ll_avg", "v_ry", "v_yb", "v_br",
            "v_ln_avg", "v_r", "v_y", "v_b",
            "current_total", "current_r", "current_y", "current_b",
            "frequency", "energy_wh", "energy_vah", "load_hours"
        ]
        
        placeholders = ", ".join(["?"] * len(cols))
        sql = f"INSERT INTO telemetry ({', '.join(cols)}) VALUES ({placeholders}) ON CONFLICT(record_id) DO NOTHING"
        
        values = (
            record.get('record_id', str(uuid.uuid4())),
            record['timestamp'],
            record.get('factory_id', 'fac_001'),
            record.get('asset_id'),
            voltage_v,
            current_a,
            active_power_kw,
            energy_kwh,
            frequency_hz,
            power_factor,
            record.get('machine_state', 'RUNNING'),
            record.get('data_source', 'SIMULATED_RASPI'),
            record.get('data_quality', 'GOOD'),
            watts_total,
            record.get('watts_r'),
            record.get('watts_y'),
            record.get('watts_b'),
            pf_avg,
            record.get('pf_r'),
            record.get('pf_y'),
            record.get('pf_b'),
            record.get('va_total'),
            record.get('va_r'),
            record.get('va_y'),
            record.get('va_b'),
            record.get('v_ll_avg'),
            record.get('v_ry'),
            record.get('v_yb'),
            record.get('v_br'),
            v_ln_avg,
            record.get('v_r'),
            record.get('v_y'),
            record.get('v_b'),
            current_total,
            record.get('current_r'),
            record.get('current_y'),
            record.get('current_b'),
            frequency,
            energy_wh,
            record.get('energy_vah'),
            record.get('load_hours')
        )

        with get_connection() as conn:
            conn.execute(sql, values)
            conn.commit()
            return True
    except Exception as e:
        print(f"DB Insert Error: {e}")
        return False

def query_telemetry(start_time: str, end_time: str, source: str = None, asset_id: str = None, limit: int = 5000, offset: int = 0) -> List[Dict[str, Any]]:
    query = "SELECT * FROM telemetry WHERE timestamp >= ? AND timestamp <= ?"
    params = [start_time, end_time]
    
    if source:
        query += " AND data_source = ?"
        params.append(source)
    if asset_id:
        query += " AND asset_id = ?"
        params.append(asset_id)
        
    query += " ORDER BY timestamp ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    with get_connection() as conn:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def count_telemetry(start_time: str, end_time: str, source: str = None, asset_id: str = None) -> int:
    query = "SELECT COUNT(*) FROM telemetry WHERE timestamp >= ? AND timestamp <= ?"
    params = [start_time, end_time]
    if source:
        query += " AND data_source = ?"
        params.append(source)
    if asset_id:
        query += " AND asset_id = ?"
        params.append(asset_id)
        
    with get_connection() as conn:
        return conn.execute(query, params).fetchone()[0]

def delete_test_run(run_id: str):
    """Safe cleanup of explicit test seeds using the run_id encoded in factory_id or similar.
       We will store run_id in factory_id as 'fac_001_test_<run_id>' for test seeds.
    """
    with get_connection() as conn:
        conn.execute("DELETE FROM telemetry WHERE factory_id LIKE ?", (f"%{run_id}%",))
        conn.commit()

# ==========================================
# ASSET REGISTRY & CONTROL DATA ACCESS
# ==========================================

import json
from datetime import datetime, timezone

def list_assets(
    include_archived: bool = False,
    search: str = None,
    classification: str = None,
    is_protected: bool = None,
    pcc: str = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    query = "SELECT * FROM assets WHERE 1=1"
    params = []

    if not include_archived:
        query += " AND is_archived = 0"
    
    if search:
        query += " AND (asset_id LIKE ? OR name LIKE ? OR equipment_type LIKE ? OR location LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])

    if classification and classification != "ALL":
        query += " AND load_classification = ?"
        params.append(classification)

    if is_protected is not None:
        query += " AND is_protected = ?"
        params.append(1 if is_protected else 0)

    if pcc and pcc != "ALL":
        query += " AND pcc_association = ?"
        params.append(pcc)

    query += " ORDER BY priority_order ASC, asset_id ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_connection() as conn:
        cursor = conn.execute(query, params)
        rows = [dict(r) for r in cursor.fetchall()]
        for r in rows:
            if isinstance(r.get("permitted_actions"), str):
                try:
                    r["permitted_actions"] = json.loads(r["permitted_actions"])
                except Exception:
                    r["permitted_actions"] = ["monitor_only"]
        return rows

def count_assets(
    include_archived: bool = False,
    search: str = None,
    classification: str = None,
    is_protected: bool = None,
    pcc: str = None
) -> int:
    query = "SELECT COUNT(*) FROM assets WHERE 1=1"
    params = []

    if not include_archived:
        query += " AND is_archived = 0"
    
    if search:
        query += " AND (asset_id LIKE ? OR name LIKE ? OR equipment_type LIKE ? OR location LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])

    if classification and classification != "ALL":
        query += " AND load_classification = ?"
        params.append(classification)

    if is_protected is not None:
        query += " AND is_protected = ?"
        params.append(1 if is_protected else 0)

    if pcc and pcc != "ALL":
        query += " AND pcc_association = ?"
        params.append(pcc)

    with get_connection() as conn:
        return conn.execute(query, params).fetchone()[0]

def get_asset(asset_id: str) -> Optional[Dict[str, Any]]:
    if not asset_id:
        return None
    query = "SELECT * FROM assets WHERE UPPER(asset_id) = UPPER(?)"
    with get_connection() as conn:
        row = conn.execute(query, (asset_id.strip(),)).fetchone()
        if not row:
            return None
        res = dict(row)
        if isinstance(res.get("permitted_actions"), str):
            try:
                res["permitted_actions"] = json.loads(res["permitted_actions"])
            except Exception:
                res["permitted_actions"] = ["monitor_only"]
        return res

def create_asset_record(data: dict) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    canonical_id = data["asset_id"].strip().upper()
    data["asset_id"] = canonical_id
    permitted_actions = data.get("permitted_actions", ["monitor_only"])
    if isinstance(permitted_actions, list):
        permitted_str = json.dumps(permitted_actions)
    else:
        permitted_str = str(permitted_actions)

    cols = [
        "asset_id", "name", "equipment_type", "manufacturer_model", "location",
        "rated_capacity_kw", "rated_voltage_v", "phase_config", "pcc_association",
        "meter_association", "load_classification", "priority_order", "is_protected",
        "permitted_actions", "min_runtime_minutes", "min_offtime_minutes",
        "restart_delay_minutes", "operating_schedule", "production_constraints",
        "operator_notes", "maintenance_notes", "is_archived", "created_at", "updated_at"
    ]
    placeholders = ", ".join(["?"] * len(cols))
    sql = f"INSERT INTO assets ({', '.join(cols)}) VALUES ({placeholders})"

    values = (
        canonical_id,
        data.get("name", canonical_id),
        data.get("equipment_type", "Not configured"),
        data.get("manufacturer_model", "Not configured"),
        data.get("location", "Not configured"),
        data.get("rated_capacity_kw"),
        data.get("rated_voltage_v"),
        data.get("phase_config", "Not configured"),
        data.get("pcc_association", "PCC-01"),
        data.get("meter_association", "RPi-METER-01"),
        data.get("load_classification", "Flexible"),
        data.get("priority_order", 2),
        1 if data.get("is_protected") else 0,
        permitted_str,
        data.get("min_runtime_minutes", 15),
        data.get("min_offtime_minutes", 15),
        data.get("restart_delay_minutes", 5),
        data.get("operating_schedule", "24/7 Continuous"),
        data.get("production_constraints", "Not configured"),
        data.get("operator_notes", "Not configured"),
        data.get("maintenance_notes", "Not configured"),
        0,
        now,
        now
    )

    with get_connection() as conn:
        conn.execute(sql, values)
        conn.commit()

    return get_asset(canonical_id)

def update_asset_record(asset_id: str, updates: dict) -> Optional[Dict[str, Any]]:
    current = get_asset(asset_id)
    if not current:
        return None

    canonical_id = current["asset_id"]

    # Disallow overriding asset_id
    updates.pop("asset_id", None)
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    if "permitted_actions" in updates and isinstance(updates["permitted_actions"], list):
        updates["permitted_actions"] = json.dumps(updates["permitted_actions"])

    if "is_protected" in updates:
        updates["is_protected"] = 1 if updates["is_protected"] else 0

    set_clauses = []
    values = []
    for k, v in updates.items():
        set_clauses.append(f"{k} = ?")
        values.append(v)
    values.append(canonical_id)

    sql = f"UPDATE assets SET {', '.join(set_clauses)} WHERE UPPER(asset_id) = UPPER(?)"

    with get_connection() as conn:
        conn.execute(sql, values)
        conn.commit()

    return get_asset(canonical_id)

def archive_asset_record(asset_id: str) -> Optional[Dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    sql = "UPDATE assets SET is_archived = 1, archived_at = ?, updated_at = ? WHERE UPPER(asset_id) = UPPER(?)"
    with get_connection() as conn:
        conn.execute(sql, (now, now, asset_id.strip()))
        conn.commit()
    return get_asset(asset_id)

def unarchive_asset_record(asset_id: str) -> Optional[Dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    sql = "UPDATE assets SET is_archived = 0, archived_at = NULL, updated_at = ? WHERE UPPER(asset_id) = UPPER(?)"
    with get_connection() as conn:
        conn.execute(sql, (now, asset_id.strip()))
        conn.commit()
    return get_asset(asset_id)

def get_control_actions_by_asset(asset_id: str) -> List[Dict[str, Any]]:
    sql = "SELECT * FROM asset_control_audit WHERE UPPER(asset_id) = UPPER(?) ORDER BY created_at DESC"
    with get_connection() as conn:
        cursor = conn.execute(sql, (asset_id.strip(),))
        return [dict(r) for r in cursor.fetchall()]

def create_control_action_record(data: dict) -> Dict[str, Any]:
    cols = [
        "action_id", "asset_id", "action_type", "recommendation_reason",
        "current_demand_kw", "threshold_kw", "expected_impact_kw",
        "production_implications", "status", "physical_verification_status"
    ]
    placeholders = ", ".join(["?"] * len(cols))
    sql = f"INSERT OR REPLACE INTO asset_control_audit ({', '.join(cols)}) VALUES ({placeholders})"
    values = (
        data["action_id"],
        data["asset_id"],
        data["action_type"],
        data.get("recommendation_reason", "Optimizer demand management"),
        data.get("current_demand_kw", 91.0),
        data.get("threshold_kw", 90.0),
        data.get("expected_impact_kw", 5.0),
        data.get("production_implications", "Advisory load modulation"),
        data.get("status", "AWAITING_APPROVAL"),
        data.get("physical_verification_status", "PENDING")
    )
    with get_connection() as conn:
        conn.execute(sql, values)
        conn.commit()
    return data

def decide_control_action(action_id: str, decision: str, operator_id: str, operator_notes: str = None) -> Optional[Dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    status = "APPROVED" if decision.upper() == "APPROVE" else "REJECTED"
    verification = "VERIFIED_OPERATOR_DISPATCH" if status == "APPROVED" else "REJECTED_BY_OPERATOR"

    sql = """
        UPDATE asset_control_audit
        SET status = ?, operator_id = ?, operator_notes = ?, decided_at = ?,
            executed_at = ?, physical_verification_status = ?
        WHERE action_id = ?
    """
    with get_connection() as conn:
        conn.execute(sql, (status, operator_id, operator_notes, now, now if status == "APPROVED" else None, verification, action_id))
        conn.commit()
        row = conn.execute("SELECT * FROM asset_control_audit WHERE action_id = ?", (action_id,)).fetchone()
        return dict(row) if row else None

init_db()

