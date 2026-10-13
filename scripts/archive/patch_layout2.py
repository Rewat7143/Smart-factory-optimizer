with open('frontend/app/layout.tsx', 'r') as f:
    content = f.read()

content = content.replace('bg-slate-950 text-slate-200', 'bg-slate-50 text-slate-900')

with open('frontend/app/layout.tsx', 'w') as f:
    f.write(content)
