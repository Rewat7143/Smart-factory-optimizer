import re

file_path = 'frontend/app/industrial-copilot/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

# Remove the boundaries
content = content.replace('\n    <ClientModeBoundary title="Industrial Copilot">\n', '')
content = content.replace('\n    </ClientModeBoundary>\n  ', '')

# Now let's wrap the MAIN return.
# The main return is right after `const insights = ...`
# Let's find: `return (\n    <div className="p-6`
main_ret = 'return (\n    <div className="p-6 font-mono space-y-6 flex flex-col h-full">'
if main_ret in content:
    wrapped_ret = 'return (\n    <ClientModeBoundary title="Industrial Copilot">\n    <div className="p-6 font-mono space-y-6 flex flex-col h-full">'
    content = content.replace(main_ret, wrapped_ret)
    
    # The last `  )\n}`
    # Let's find the last `  )\n}` and replace with `    </ClientModeBoundary>\n  )\n}`
    idx = content.rfind('  )\n}')
    if idx != -1:
        content = content[:idx] + '    </ClientModeBoundary>\n' + content[idx:]
        
with open(file_path, 'w') as f:
    f.write(content)

