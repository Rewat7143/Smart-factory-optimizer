import os
import re

files_to_patch = [
    'frontend/app/live-command/page.tsx',
    'frontend/app/live-twin/page.tsx',
    'frontend/app/live-quality/page.tsx',
    'frontend/app/live-economics/page.tsx',
    'frontend/app/live-copilot/page.tsx'
]

for file_path in files_to_patch:
    with open(file_path, 'r') as f:
        content = f.read()

    # Remove import
    content = re.sub(r"import \{ ClientModeBoundary \}.*\n", "", content)

    # Remove wrapper
    content = content.replace("<ClientModeBoundary>", "")
    content = content.replace("</ClientModeBoundary>", "")

    with open(file_path, 'w') as f:
        f.write(content)
    print(f"Stripped {file_path}")

