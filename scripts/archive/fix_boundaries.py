import os
import re

for root, _, files in os.walk('frontend/app'):
    for file in files:
        if file.endswith('.tsx'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            
            # Remove <ClientModeBoundary ...>
            content = re.sub(r"<ClientModeBoundary[^>]*>", "", content)
            
            with open(path, 'w') as f:
                f.write(content)

