import os
import re

pages_to_patch = [
    ('frontend/app/verified-ledger/page.tsx', 'Verified Ledger'),
    ('frontend/app/scale-simulator/page.tsx', 'Scale Impact'),
    ('frontend/app/energy-economics/page.tsx', 'Energy Loss Map'),
    ('frontend/app/forecast/page.tsx', 'Intelligence (Eng)'),
    ('frontend/app/predictive-maintenance/page.tsx', 'Predictive Maintenance'),
    ('frontend/app/industrial-copilot/page.tsx', 'Industrial Copilot')
]

for file_path, title in pages_to_patch:
    if not os.path.exists(file_path):
        continue
    with open(file_path, 'r') as f:
        content = f.read()
        
    # Remove my bad injections
    # I injected: \n    <ClientModeBoundary title="{title}">\n
    bad_start = f'\n    <ClientModeBoundary title="{title}">\n'
    bad_end = f'\n    </ClientModeBoundary>\n'
    
    content = content.replace(bad_start, '')
    content = content.replace(bad_end, '')
    
    # Now let's do it properly! 
    # I will look for the very LAST "return (" in the file.
    
    parts = content.rsplit('return (', 1)
    if len(parts) == 2:
        top_half = parts[0]
        bottom_half = parts[1]
        
        last_paren_idx = bottom_half.rfind(')')
        if last_paren_idx != -1:
            inner_content = bottom_half[:last_paren_idx]
            remainder = bottom_half[last_paren_idx:]
            
            wrapped = f'\n    <ClientModeBoundary title="{title}">\n{inner_content}\n    </ClientModeBoundary>\n  '
            new_content = top_half + 'return (' + wrapped + remainder
            
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"Fixed {file_path}")
            
