import re

with open('frontend/app/optimization-lab/page.tsx', 'r') as f:
    content = f.read()

content = 'import { ClientModeBoundary } from "@/components/ClientModeBoundary"\n' + content

match = re.search(r'return\s*\(\s*(<div.*)\)\s*$', content, re.DOTALL)
if match:
    inner = match.group(1)
    wrapped = f'return (\n    <ClientModeBoundary title="Optimization (Eng)">\n      {inner}    </ClientModeBoundary>\n  )'
    content = content[:match.start()] + wrapped + content[match.end():]
    
with open('frontend/app/optimization-lab/page.tsx', 'w') as f:
    f.write(content)
