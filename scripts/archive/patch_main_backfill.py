import re

file_path = 'backend/main.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """from api.backfill import ensure_commissioning_data

@app.on_event("startup")
def startup_event():
    logger.info("Starting up Smart Factory Optimizer Backend...")
    gsheets_db.connect()
    ensure_commissioning_data()
    asyncio.create_task(background_telemetry_flush())"""

pattern = r'@app\.on_event\("startup"\)\ndef startup_event\(\).*?asyncio\.create_task\(background_telemetry_flush\(\)\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
