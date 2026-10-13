import os
import re

def scale_classes(content):
    # Scale up small text
    content = content.replace("text-[9px]", "text-sm font-black")
    content = content.replace("text-[10px]", "text-base font-black")
    content = content.replace("text-xs", "text-base font-bold")
    content = content.replace("text-sm", "text-lg font-bold")
    
    # Scale up headers and numbers
    content = content.replace("text-xl", "text-4xl font-black")
    content = content.replace("text-2xl", "text-5xl font-black")
    content = content.replace("text-3xl", "text-6xl font-black")
    
    # Scale up padding and borders for thicker industrial look
    content = content.replace("p-4", "p-6")
    content = content.replace("p-3", "p-5")
    content = content.replace("border ", "border-2 ")
    
    # Fix potential Sidebar overflow if it got too big
    # Sidebar width w-64 -> w-80
    content = content.replace("w-64", "w-80")
    
    return content

directories = ['frontend/components', 'frontend/app']

for root, _, files in os.walk('frontend'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            
            original = content
            content = scale_classes(content)
                
            if content != original:
                with open(path, 'w') as f:
                    f.write(content)
