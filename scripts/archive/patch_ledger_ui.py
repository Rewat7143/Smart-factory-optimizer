import re

file_path = 'frontend/app/verified-ledger/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

content = content.replace("Validated per ISO-50001 Energy Management Guidelines", "Awaiting sufficient empirical data for verification")

with open(file_path, 'w') as f:
    f.write(content)
