import re

file_path = 'frontend/app/energy-economics/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

content = content.replace('import React, { useEffect, useState } from \'react\'', 
                        'import React from \'react\'\nimport { useCachePoller } from "@/hooks/useCachePoller"')

pattern = r'const \[data, setData\] = useState.*?return \(\) => clearInterval\(int\);\n  \}, \[\]\);'

replacement = "const data = useCachePoller('/factory/state', 5000);"

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
