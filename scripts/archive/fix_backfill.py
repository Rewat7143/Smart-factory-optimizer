import re

file_path = 'backend/api/backfill.py'
with open(file_path, 'r') as f:
    content = f.read()

content = content.replace("from schemas.models import", "from schemas.energy import")
content = content.replace("from schemas.energy import TelemetryPayload", "from api.telemetry import TelemetryPayload")
content = content.replace("from schemas.energy import EnergyReading", "from schemas.energy import EnergyReading")

with open(file_path, 'w') as f:
    f.write(content)
