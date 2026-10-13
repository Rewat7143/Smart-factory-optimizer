import os
import re

directories = ['frontend/components', 'frontend/app']

replacements = {
    # Remove light grey text, make it dark and legible
    "text-slate-400": "text-slate-700",
    "text-slate-500": "text-slate-800",
    "text-slate-600": "text-slate-800",
    "opacity-70": "opacity-100",
    "opacity-80": "opacity-100",
    "opacity-90": "opacity-100",
    
    # Fix the Sidebar width that caused squishing
    "w-80": "w-64 flex-shrink-0",
    
    # Fix aggressive scaling that caused overflow
    "text-7xl": "text-4xl lg:text-5xl",
    "text-6xl": "text-3xl lg:text-4xl",
    "text-5xl": "text-2xl lg:text-3xl",
    "text-4xl": "text-xl lg:text-2xl",
    "p-6": "p-4",
    "p-8": "p-5",
    
    # If there's blue bg with dark text anywhere, force text-white
    "bg-teal-700": "bg-teal-700 text-white",
    "bg-emerald-600": "bg-emerald-600 text-white",
    "bg-red-600": "bg-red-600 text-white",
    "bg-indigo-700": "bg-indigo-700 text-white",
    "text-white text-white": "text-white", # clean up double classes
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
