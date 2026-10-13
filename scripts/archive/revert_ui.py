import os
import re

directories = ['frontend/components', 'frontend/app']

reversals = {
    "bg-slate-900": "bg-white",
    "border-slate-700": "border-slate-200",
    "border-slate-800": "border-slate-100",
    "text-white": "text-slate-900",
    "text-slate-100": "text-slate-800",
    "text-slate-300": "text-slate-700",
    "text-slate-400": "text-slate-600",
    "bg-slate-800": "bg-slate-50",
    "shadow-lg shadow-black/40": "shadow-sm",
    "from-slate-900 to-emerald-900/20": "from-white to-green-50/30",
    "from-slate-900 to-slate-800": "from-slate-50 to-slate-100",
}

for root, _, files in os.walk('frontend'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            
            original = content
            # To avoid order-of-operations bugs, just replace them directly
            for old, new in reversals.items():
                content = content.replace(old, new)
                
            if content != original:
                with open(path, 'w') as f:
                    f.write(content)

