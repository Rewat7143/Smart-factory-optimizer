import os
import re

pages_to_patch = [
    ('frontend/app/verified-ledger/page.tsx', 'Verified Ledger'),
    ('frontend/app/scale-simulator/page.tsx', 'Scale Impact'),
    ('frontend/app/energy-economics/page.tsx', 'Energy Loss Map'),
    ('frontend/app/forecast/page.tsx', 'Intelligence (Eng)'),
    ('frontend/app/optimization-lab/page.tsx', 'Optimization (Eng)'),
    ('frontend/app/predictive-maintenance/page.tsx', 'Predictive Maintenance'),
    ('frontend/app/industrial-copilot/page.tsx', 'Industrial Copilot')
]

import_statement = 'import { ClientModeBoundary } from "@/components/ClientModeBoundary"\n'

for file_path, title in pages_to_patch:
    if not os.path.exists(file_path):
        print(f"Skipping {file_path}")
        continue
        
    with open(file_path, 'r') as f:
        content = f.read()
        
    if 'ClientModeBoundary' in content:
        continue
        
    # Inject import
    content = content.replace('"use client"\n', f'"use client"\n{import_statement}')
    if '"use client"' not in content:
        # Some might not have "use client" at top
        content = import_statement + content
        
    # Wrap return statement
    # We find `return (` and `  )` at the end
    # This is tricky using regex for a whole file.
    
    # Let's find the last `)` in the file, or just use regex to wrap the top level JSX.
    # Usually it's like:
    # return (
    #   <div className="...">
    #     ...
    #   </div>
    # )
    
    match = re.search(r'return\s*\(\s*(<div[^>]*>.*)\)\s*$', content, re.DOTALL)
    if match:
        inner = match.group(1)
        wrapped = f'return (\n    <ClientModeBoundary title="{title}">\n      {inner}    </ClientModeBoundary>\n  )'
        content = content[:match.start()] + wrapped + content[match.end():]
        
    with open(file_path, 'w') as f:
        f.write(content)
        
    print(f"Patched {file_path}")
