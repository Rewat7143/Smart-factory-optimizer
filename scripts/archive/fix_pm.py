import re

file_path = 'frontend/app/predictive-maintenance/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

# Remove the bad boundaries
content = content.replace('\n    <ClientModeBoundary title="Predictive Maintenance">\n', '')
content = content.replace('\n    </ClientModeBoundary>\n  ', '')

# Wrap the MAIN return
main_ret = 'return (\n    <div className="max-w-[1600px] mx-auto p-4 lg:p-6 space-y-6 font-mono text-slate-800">'
if main_ret in content:
    wrapped_ret = 'return (\n    <ClientModeBoundary title="Predictive Maintenance">\n    <div className="max-w-[1600px] mx-auto p-4 lg:p-6 space-y-6 font-mono text-slate-800">'
    content = content.replace(main_ret, wrapped_ret)
    
    idx = content.rfind('  )\n}')
    if idx != -1:
        content = content[:idx] + '    </ClientModeBoundary>\n' + content[idx:]
        
with open(file_path, 'w') as f:
    f.write(content)

