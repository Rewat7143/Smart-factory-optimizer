import re

file_path = 'backend/main.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """from api.backfill import ensure_commissioning_data

@app.on_event("startup")
def startup_event():
    gsheets_db.connect()
    ensure_commissioning_data()
    simulation_controller.start()
    asyncio.create_task(continuous_learning_loop())"""

pattern = r'@app\.on_event\("startup"\)\ndef startup_event\(\):\n\s*gsheets_db\.connect\(\)\n\s*simulation_controller\.start\(\)\n\s*asyncio\.create_task\(continuous_learning_loop\(\)\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
