import re

file_path = 'frontend/app/predictive-maintenance/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

# We know it doesn't have the ClientModeBoundary right now because my last script removed it, but failed to inject it back!
# Let's double check it doesn't have it.
content = content.replace('<ClientModeBoundary title="Predictive Maintenance">', '')
content = content.replace('</ClientModeBoundary>', '')

main_ret = 'return (\n    <div className="p-6 font-mono space-y-6">'
wrapped_ret = 'return (\n    <ClientModeBoundary title="Predictive Maintenance">\n    <div className="p-6 font-mono space-y-6">'

content = content.replace(main_ret, wrapped_ret)

idx = content.rfind('  )\n}')
if idx != -1:
    content = content[:idx] + '    </ClientModeBoundary>\n' + content[idx:]
    
with open(file_path, 'w') as f:
    f.write(content)

