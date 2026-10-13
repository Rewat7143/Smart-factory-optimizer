from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

try:
    res = client.get("/api/maintenance/status")
    print("STATUS:", res.status_code)
    print("BODY:", json.dumps(res.json(), indent=2)[:500])
except Exception as e:
    import traceback
    traceback.print_exc()
