with open('frontend/components/LiveMeterPlaceholder.tsx', 'r') as f:
    content = f.read()

import re
content = re.sub(r'(font-bold )+', 'font-bold ', content)
content = content.replace('text-xl lg:text-2xl font-bold text-slate-800 uppercase tracking-tight', 'text-4xl lg:text-5xl font-bold text-slate-800 uppercase tracking-tight')
content = content.replace('text-xl lg:text-2xl font-bold', 'text-2xl font-bold')
content = content.replace('text-base font-bold text-slate-800 uppercase font-bold tracking-widest', 'text-xs font-semibold uppercase tracking-widest text-slate-500')
content = content.replace('text-base font-bold text-emerald-400 uppercase font-bold tracking-widest', 'text-xs font-semibold uppercase tracking-widest text-emerald-600')
content = content.replace('border-2 border-slate-100', 'border border-slate-200')
content = content.replace('border-2 border-slate-200', 'border border-slate-200')
content = content.replace('bg-emerald-500/10', 'bg-emerald-50')
content = content.replace('border-emerald-500/30', 'border-emerald-200')
content = content.replace('text-emerald-400', 'text-emerald-600')

with open('frontend/components/LiveMeterPlaceholder.tsx', 'w') as f:
    f.write(content)
