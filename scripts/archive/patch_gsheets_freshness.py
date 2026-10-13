import re

file_path = 'backend/api/telemetry.py'
with open(file_path, 'r') as f:
    content = f.read()

content = content.replace("if age >= -5:", "if -5 <= age <= 60:  # Must be genuinely fresh to act as live telemetry")

with open(file_path, 'w') as f:
    f.write(content)
