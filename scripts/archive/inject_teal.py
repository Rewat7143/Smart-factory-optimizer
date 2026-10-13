import os
import re

directories = ['frontend/components', 'frontend/app']

replacements = {
    "text-blue-600": "text-teal-700",
    "bg-blue-600": "bg-teal-700",
    "border-blue-200": "border-teal-200",
    "bg-blue-50": "bg-teal-50",
    "text-blue-900": "text-teal-900",
    "text-blue-500": "text-teal-600",
    "bg-blue-500": "bg-teal-600",
    "text-blue-400": "text-teal-500",
    "border-blue-400": "border-teal-400",
    "text-slate-900": "text-slate-800", # slightly softer industrial text
}

for root, _, files in os.walk('frontend'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            
            original = content
            for old, new in replacements.items():
                content = content.replace(old, new)
                
            if content != original:
                with open(path, 'w') as f:
                    f.write(content)
