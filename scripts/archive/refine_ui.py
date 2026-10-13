import os
import re

directories = ['frontend/components', 'frontend/app']

replacements = {
    # Scale down extreme text sizes
    "text-7xl lg:text-9xl": "text-5xl lg:text-7xl",
    "text-5xl lg:text-7xl": "text-4xl lg:text-5xl",
    "text-4xl lg:text-5xl": "text-3xl lg:text-4xl",
    "text-3xl lg:text-4xl": "text-2xl lg:text-3xl",
    "text-2xl lg:text-3xl": "text-xl lg:text-2xl",
    "text-7xl": "text-5xl",
    "text-6xl": "text-4xl",
    "text-5xl": "text-3xl",
    "text-4xl": "text-2xl",
    "text-3xl": "text-xl",
    
    # Refine typography (less screaming 'black', more sophisticated 'semibold'/'bold')
    "font-black": "font-bold",
    "tracking-tighter": "tracking-tight",
    
    # Refine borders and shadows (remove cartoonish border-4, use elegant borders)
    "border-4": "border",
    "shadow-xl": "shadow-sm hover:shadow transition-shadow",
    "shadow-2xl": "shadow-md",
    "rounded-2xl": "rounded-xl",
    "p-8": "p-6",
    
    # Specific UI Fixes
    # 1. Strikethrough removal in CommandCenter
    "line-through decoration-red-500 decoration-4": "opacity-70 font-medium",
    
    # 2. WASTE text in Energy Loss Map
    "bg-red-500 opacity-50 relative": "bg-red-100 border-l-2 border-red-500 relative",
    "text-xs font-black text-white": "text-xs font-bold text-red-700 tracking-widest",
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
                
            # Additional sophisticated label styling
            # Replace: text-lg uppercase tracking-widest text-slate-800
            # With: text-xs uppercase tracking-widest font-semibold text-slate-500
            content = re.sub(r'text-(lg|xl) font-bold uppercase tracking-widest text-slate-([87]00)', r'text-xs font-bold uppercase tracking-widest text-slate-500', content)
            
            if content != original:
                with open(path, 'w') as f:
                    f.write(content)

