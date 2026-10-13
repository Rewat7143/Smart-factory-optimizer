import re

file_path = 'backend/main.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
app.include_router(telemetry.router, prefix="/api")
from api import control
app.include_router(control.router, prefix="/api")
"""

pattern = r'app\.include_router\(telemetry\.router, prefix="/api"\)'
content = re.sub(pattern, replacement, content, count=1)

with open(file_path, 'w') as f:
    f.write(content)
