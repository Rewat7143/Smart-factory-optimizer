import re

files = {
    'frontend/app/predictive-maintenance/page.tsx': {
        'url': '/maintenance/status',
        'interval': 5000,
        'state_name': 'data',
        'func_name': 'fetchMaint'
    },
    'frontend/app/industrial-copilot/page.tsx': {
        'url': '/copilot/insights',
        'interval': 5000,
        'state_name': 'data',
        'func_name': 'fetchCopilot'
    },
    'frontend/app/verified-ledger/page.tsx': {
        'url': '/factory/state',
        'interval': 5000,
        'state_name': 'data',
        'func_name': 'fetchData'
    }
}

for file_path, cfg in files.items():
    with open(file_path, 'r') as f:
        content = f.read()
        
    # Inject import
    if 'useCachePoller' not in content:
        content = content.replace('import React, { useEffect, useState } from \'react\'', 
                                'import React from \'react\'\nimport { useCachePoller } from "@/hooks/useCachePoller"')
        content = content.replace('import React, { useState, useEffect } from \'react\'', 
                                'import React from \'react\'\nimport { useCachePoller } from "@/hooks/useCachePoller"')
        
        # We want to replace:
        # const [data, setData] = useState<any>(null);
        # useEffect(() => { ... }, []);
        
        # Regex to match the block
        pattern = r'const \[' + cfg['state_name'] + r', set[A-Z]\w+\] = useState<any>\(.*?\);\s*useEffect\(\(\) => \{.*?\},\s*\[\]\);'
        
        replacement = f"const {cfg['state_name']} = useCachePoller('{cfg['url']}', {cfg['interval']});"
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"Rewrote {file_path}")

