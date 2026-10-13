import os

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
        
    # Skip if already wrapped
    if f'<ClientModeBoundary title="{title}">' in content:
        continue
        
    # Find the FIRST "return (" after the component declaration
    # And we just insert the opening tag right after "return ("
    # And then we find the LAST ")" and insert the closing tag right before it.
    
    parts = content.split('return (', 1)
    if len(parts) == 2:
        top_half = parts[0]
        bottom_half = parts[1]
        
        # Bottom half contains everything inside and after return (...)
        # The last ) before } is what we want.
        last_paren_idx = bottom_half.rfind(')')
        
        if last_paren_idx != -1:
            inner_content = bottom_half[:last_paren_idx]
            remainder = bottom_half[last_paren_idx:]
            
            wrapped = f'\n    <ClientModeBoundary title="{title}">\n{inner_content}\n    </ClientModeBoundary>\n'
            
            new_content = top_half + 'return (' + wrapped + remainder
            
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"Patched {file_path}")

