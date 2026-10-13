import re

file_path = 'frontend/app/layout.tsx'
with open(file_path, 'r') as f:
    content = f.read()

import_line = 'import { BackgroundPoller } from "@/components/BackgroundPoller";\n'
content = content.replace('import { SidebarNav } from "@/components/SidebarNav";\n', 
                          'import { SidebarNav } from "@/components/SidebarNav";\n' + import_line)

# Insert <BackgroundPoller /> inside GlobalStateProvider
content = content.replace('<GlobalStateProvider>\n', '<GlobalStateProvider>\n          <BackgroundPoller />\n')

with open(file_path, 'w') as f:
    f.write(content)
    
