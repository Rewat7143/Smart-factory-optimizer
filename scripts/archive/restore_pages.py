import re

files = [
    'frontend/app/verified-ledger/page.tsx',
    'frontend/app/scale-simulator/page.tsx',
    'frontend/app/energy-economics/page.tsx',
    'frontend/app/forecast/page.tsx',
    'frontend/app/predictive-maintenance/page.tsx',
    'frontend/app/industrial-copilot/page.tsx'
]

for file_path in files:
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Use regex to strip out the ClientModeBoundary wrapper but keep the inner content!
    # Because there might be a title prop, we use a robust regex.
    # The pattern is `<ClientModeBoundary title=".*?">` and `</ClientModeBoundary>`
    
    # 1. Remove the opening tag
    content = re.sub(r'<ClientModeBoundary[^>]*>\s*', '', content)
    # 2. Remove the closing tag
    content = re.sub(r'\s*</ClientModeBoundary>\s*', '\n', content)
    
    # 3. If there is an unused import, remove it to prevent lint errors
    content = re.sub(r'import\s+{\s*ClientModeBoundary\s*}\s*from\s*"@/components/ClientModeBoundary"\n', '', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
        
    print(f"Restored {file_path}")

