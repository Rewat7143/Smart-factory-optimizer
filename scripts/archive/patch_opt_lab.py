import re

file_path = 'frontend/app/optimization-lab/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

# 1. Remove ClientModeBoundary
content = re.sub(r'<ClientModeBoundary[^>]*>\s*', '', content)
content = re.sub(r'\s*</ClientModeBoundary>\s*', '\n', content)
content = re.sub(r'import\s+{\s*ClientModeBoundary\s*}\s*from\s*"@/components/ClientModeBoundary"\n', '', content)

# 2. Swap to useCachePoller
content = content.replace('import React, { useState, useEffect } from \'react\'', 'import React from \'react\'\nimport { useCachePoller } from "@/hooks/useCachePoller"')

fetch_pattern = r'const \[pipeline, setPipeline\] = useState.*?clearTimeout\(tid\);\s*\}\n  \}, \[\]\)'
new_fetch = """const pipeline = useCachePoller('/optimize', 2000)
  const factoryState = useCachePoller('/factory/state', 2000)"""

content = re.sub(fetch_pattern, new_fetch, content, flags=re.DOTALL)

# 3. Fix demoState references
content = content.replace('demoState', 'factoryState')

# 4. Handle UNAVAILABLE from backend
if_pattern = r'if \(!pipeline \|\| !factoryState\) return <div className="p-10 font-mono text-slate-800">INITIALIZING AI OPTIMIZER\.\.\.</div>'
new_if = """if (!pipeline || !factoryState) return <div className="p-10 font-mono text-slate-800">INITIALIZING AI OPTIMIZER...</div>
  if (pipeline.status === 'UNAVAILABLE') return (
     <div className="max-w-[1600px] mx-auto p-10 font-mono text-slate-800 space-y-4">
        <h1 className="text-3xl font-bold uppercase text-red-600">Optimization Unavailable</h1>
        <p className="font-semibold">{pipeline.reason}</p>
     </div>
  )"""
content = content.replace(if_pattern, new_if)

with open(file_path, 'w') as f:
    f.write(content)
