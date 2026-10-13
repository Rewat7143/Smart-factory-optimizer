import os
import glob

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        
    # Replace hardcoded API_URL fallbacks with dynamic window location
    if "process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'" in content:
        replacement = "(typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))"
        content = content.replace("process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'", replacement)
        
    with open(filepath, 'w') as f:
        f.write(content)

for root, _, files in os.walk('frontend'):
    for file in files:
        if file.endswith(('.ts', '.tsx')):
            patch_file(os.path.join(root, file))

