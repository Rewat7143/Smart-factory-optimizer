import re

file_path = 'backend/api/telemetry.py'
with open(file_path, 'r') as f:
    content = f.read()

content = content.replace('    }\n    }\n\n@router.get("/telemetry/source-status")', '    }\n\n@router.get("/telemetry/source-status")')

with open(file_path, 'w') as f:
    f.write(content)
