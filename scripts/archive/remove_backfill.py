import re

file_path = 'backend/main.py'
with open(file_path, 'r') as f:
    content = f.read()

# Remove the import and the call
content = re.sub(r'from api\.backfill import ensure_commissioning_data\n', '', content)
content = re.sub(r'\s*ensure_commissioning_data\(\)\n', '\n', content)

with open(file_path, 'w') as f:
    f.write(content)
