import os
import re

directories = ['frontend/components', 'frontend/app']

replacements = {
    "bg-white": "bg-slate-900",
    "border-slate-200": "border-slate-700",
    "border-slate-100": "border-slate-800",
    "text-slate-900": "text-white",
    "text-slate-800": "text-slate-100",
    "text-slate-700": "text-slate-300",
    "text-slate-600": "text-slate-400",
    "bg-slate-50": "bg-slate-800",
    "bg-slate-100": "bg-slate-800",
    "shadow-sm": "shadow-lg shadow-black/40",
    "from-white to-green-50/30": "from-slate-900 to-emerald-900/20",
    "from-slate-50 to-slate-100": "from-slate-900 to-slate-800",
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
                
            # If OFFLINE handling is needed, let's inject a global replacement for `{0}` to `{state.live_status === 'OFFLINE' ? '####' : 0}` but that's too brittle.
            # We'll just leave it as 0.0 with the dark theme.
                
            if content != original:
                with open(path, 'w') as f:
                    f.write(content)

