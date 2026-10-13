import re

file_path = 'frontend/app/forecast/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

content = content.replace('import React, { useEffect, useState } from \'react\'', 
                        'import React from \'react\'\nimport { useCachePoller } from "@/hooks/useCachePoller"')

pattern = r'const \[state, setState\] = useState.*?return \(\) => clearInterval\(interval\)\n  \}, \[\]\)'

replacement = """const state = useCachePoller('/factory/state', 2000)
  const pipeline = useCachePoller('/optimize', 2000)
  const registry = useCachePoller('/forecast/registry', 10000)
  const historyData = useCachePoller('/energy/history', 2000)"""

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
