import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from config import TelemetryConfig, config as default_config
from meter_reader import MeterReadResult

import math

def safe_float(val: Any, default: float = 0.0) -> float:
    """Ensures values are strictly finite floats, converting NaN/Inf/None to clean default."""
    if val is None:
        return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f) or abs(f) > 1e12:
            return default
        return f
    except (ValueError, TypeError):
        return default

class TelemetryNormalizer:
    """
    Normalizes raw L&T WL 4400 readings into canonical payloads for:
    1. Existing FastAPI Backend Ingestion API (`POST /api/telemetry/ingest`)
    2. Existing Google Sheets `TELEMETRY` tab
    """
    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or default_config

    def normalize(self, read_result: MeterReadResult) -> Dict[str, Any]:
        """
        Transforms a MeterReadResult into an authoritative telemetry packet.
        """
        record_id = str(uuid.uuid4())
        now_utc = datetime.now(timezone.utc)
        timestamp_str = now_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        if not read_result.success:
            # Explicit failure packet (Never fabricate data!)
            return {
                "record_id": record_id,
                "timestamp": timestamp_str,
                "source": "RASPBERRY_PI" if not read_result.is_mock else "SIMULATED_RASPI",
                "device_id": self.config.device_id,
                "voltage": 0.0,
                "current": 0.0,
                "active_power_kw": 0.0,
                "energy_kwh": 0.0,
                "frequency_hz": 50.0,
                "power_factor": 1.0,
                "quality": "BAD",
                "machine_state": "IDLE",
                "communication_error": read_result.error or "Meter communication failure",
                "raw_parameters": {}
            }

        raw = read_result.data
        source_name = "SIMULATED_RASPI" if read_result.is_mock else "RASPBERRY_PI"

        # Derived aggregated parameters with strict safe_float sanitization
        watts_total = safe_float(raw.get("watts_total"), 0.0)
        active_power_kw = round(watts_total / 1000.0, 4)

        energy_wh = safe_float(raw.get("energy_wh"), 0.0)
        energy_kwh = round(energy_wh / 1000.0, 4)

        v_ln_avg = safe_float(raw.get("v_ln_avg"), 0.0)
        current_total = safe_float(raw.get("current_total"), 0.0)
        pf_avg = safe_float(raw.get("pf_avg"), 1.0)
        frequency = safe_float(raw.get("frequency"), 50.0)

        # Quality validation
        quality = "GOOD"
        if not (150.0 <= v_ln_avg <= 300.0) or not (45.0 <= frequency <= 55.0) or not (-1.0 <= pf_avg <= 1.0):
            quality = "WARNING"

        # Machine state heuristic based on current flow
        machine_state = "RUNNING" if current_total > 0.5 and active_power_kw > 0.2 else "IDLE"

        payload = {
            "record_id": record_id,
            "timestamp": timestamp_str,
            "source": source_name,
            "device_id": self.config.device_id,
            
            # Compatibility & aggregated fields
            "voltage": round(v_ln_avg, 2),
            "current": round(current_total, 2),
            "active_power_kw": active_power_kw,
            "energy_kwh": energy_kwh,
            "frequency_hz": round(frequency, 2),
            "power_factor": round(pf_avg, 3),
            "quality": quality,
            "machine_state": machine_state,

            # Complete 27 memory map parameters preserved with safe_float
            "watts_total": watts_total,
            "watts_r": safe_float(raw.get("watts_r"), 0.0),
            "watts_y": safe_float(raw.get("watts_y"), 0.0),
            "watts_b": safe_float(raw.get("watts_b"), 0.0),

            "pf_avg": pf_avg,
            "pf_r": safe_float(raw.get("pf_r"), 1.0),
            "pf_y": safe_float(raw.get("pf_y"), 1.0),
            "pf_b": safe_float(raw.get("pf_b"), 1.0),

            "va_total": safe_float(raw.get("va_total"), 0.0),
            "va_r": safe_float(raw.get("va_r"), 0.0),
            "va_y": safe_float(raw.get("va_y"), 0.0),
            "va_b": safe_float(raw.get("va_b"), 0.0),

            "v_ll_avg": safe_float(raw.get("v_ll_avg"), 0.0),
            "v_ry": safe_float(raw.get("v_ry"), 0.0),
            "v_yb": safe_float(raw.get("v_yb"), 0.0),
            "v_br": safe_float(raw.get("v_br"), 0.0),

            "v_ln_avg": v_ln_avg,
            "v_r": safe_float(raw.get("v_r"), 0.0),
            "v_y": safe_float(raw.get("v_y"), 0.0),
            "v_b": safe_float(raw.get("v_b"), 0.0),

            "current_total": current_total,
            "current_r": safe_float(raw.get("current_r"), 0.0),
            "current_y": safe_float(raw.get("current_y"), 0.0),
            "current_b": safe_float(raw.get("current_b"), 0.0),

            "frequency": frequency,
            "energy_wh": energy_wh,
            "energy_vah": safe_float(raw.get("energy_vah"), 0.0),
            "load_hours": int(safe_float(raw.get("load_hours"), 0.0))
        }
        return payload

    def to_sheets_row(self, payload: Dict[str, Any]) -> List[Any]:
        """
        Formats normalized packet into the exact 12-column header of existing Google Sheet `TELEMETRY`:
        ['record_id', 'timestamp', 'source', 'device_id', 'voltage', 'current', 
         'active_power_kw', 'energy_kwh', 'frequency_hz', 'power_factor', 'quality', 'machine_state']
        """
        return [
            str(payload.get("record_id", "")),
            str(payload.get("timestamp", "")),
            str(payload.get("source", "RASPBERRY_PI")),
            str(payload.get("device_id", self.config.device_id)),
            float(payload.get("voltage", 0.0)),
            float(payload.get("current", 0.0)),
            float(payload.get("active_power_kw", 0.0)),
            float(payload.get("energy_kwh", 0.0)),
            float(payload.get("frequency_hz", 0.0)),
            float(payload.get("power_factor", 0.0)),
            str(payload.get("quality", "GOOD")),
            str(payload.get("machine_state", "RUNNING"))
        ]
