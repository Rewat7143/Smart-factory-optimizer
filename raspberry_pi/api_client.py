import math
import logging
import requests
from typing import Dict, Any, List, Tuple, Optional
from config import TelemetryConfig, config as default_config

logger = logging.getLogger("ApiClient")


def sanitize_json(val: Any) -> Any:
    """Ensures payloads are 100% compliant with standard JSON (no NaN or Inf)."""
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val) or abs(val) > 1e12:
            return 0.0
        return val
    elif isinstance(val, dict):
        return {k: sanitize_json(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [sanitize_json(v) for v in val]
    return val


class ApplicationApiClient:
    """
    HTTP client for the existing Smart Factory Energy Autopilot FastAPI backend.
    Sends telemetry to POST /api/telemetry/ingest and checks health at /api/system/status.
    """
    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or default_config
        self.session = requests.Session()

    def check_health(self) -> Tuple[bool, Optional[str]]:
        """Checks if the FastAPI backend is running and healthy."""
        url = self.config.get_health_url()
        try:
            resp = self.session.get(url, timeout=self.config.api_timeout_seconds)
            if resp.status_code == 200:
                return True, "ONLINE"
            return False, f"HTTP {resp.status_code}: {resp.text}"
        except requests.exceptions.RequestException as e:
            return False, f"Connection failed: {e}"

    def send_telemetry(self, payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Sends a single telemetry reading to the ingestion endpoint.
        Returns (success: bool, error_message: Optional[str]).
        """
        url = self.config.get_ingest_url()
        clean_payload = sanitize_json(payload)
        try:
            resp = self.session.post(
                url,
                json=clean_payload,
                timeout=self.config.api_timeout_seconds
            )
            if resp.status_code == 200:
                data = resp.json()
                self.last_response_data = data
                if data.get("accepted"):
                    return True, None
                return False, f"Server returned accepted=False: {data}"
            return False, f"HTTP {resp.status_code}: {resp.text}"
        except requests.exceptions.Timeout:
            return False, f"Request timed out ({self.config.api_timeout_seconds}s)"
        except requests.exceptions.ConnectionError as ce:
            return False, f"Connection refused ({ce})"
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {e}"

    def send_batch(self, payloads: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """
        Iterates over queued payloads and transmits them sequentially.
        Returns (successful_record_ids, failed_record_ids).
        """
        successful_ids = []
        failed_ids = []

        for p in payloads:
            rec_id = p.get("record_id")
            clean_p = sanitize_json(p)
            success, err = self.send_telemetry(clean_p)
            if success:
                successful_ids.append(rec_id)
            else:
                failed_ids.append(rec_id)
                logger.warning(f"Failed to ingest event {rec_id}: {err}")
                # If network error or timeout, stop early to avoid blocking the real-time acquisition loop
                err_lower = (err or "").lower()
                if "connection refused" in err_lower or "connection failed" in err_lower or "timed out" in err_lower:
                    break

        return successful_ids, failed_ids
