import re

file_path = 'frontend/components/DigitalTwin.tsx'
with open(file_path, 'r') as f:
    content = f.read()

content = content.replace('import React, { useEffect, useState } from \'react\'', 'import React from \'react\'\nimport { useCachePoller } from "@/hooks/useCachePoller"')
content = content.replace("import { getFactoryState } from '@/lib/api'\n", "")

pattern = r'const \[factory, setFactory\] = useState.*?if \(timeoutId\) clearTimeout\(timeoutId\);\n    \};\n  \}, \[\]\);'

new_hook = "const factory = useCachePoller('/factory/state', 2000);"

content = re.sub(pattern, new_hook, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
