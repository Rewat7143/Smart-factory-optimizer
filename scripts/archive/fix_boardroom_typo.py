with open('frontend/components/CommandCenter.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    '<h1 className="text-xl lg:text-2xl font-bold tracking-tight text-slate-800 uppercase">Executive Boardroom</h1>',
    '<h1 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-800 uppercase">Command Center</h1>'
)
content = content.replace(
    '<p className="text-lg lg:text-xl font-bold tracking-widest text-slate-800 uppercase mt-2">',
    '<p className="text-sm font-semibold tracking-widest text-slate-500 uppercase mt-2">'
)
content = content.replace('border-b-4 border-slate-300 pb-6', 'border-b border-slate-300 pb-4')
content = content.replace('text-2xl font-bold', 'text-xl font-bold')
content = content.replace('text-xl font-bold text-slate-800 mb-2', 'text-3xl font-bold text-slate-800 mb-2')
content = content.replace('text-2xl text-slate-600', 'text-base text-slate-500 font-semibold')
content = content.replace('divide-x-2 divide-slate-300', 'divide-x divide-slate-200')
content = content.replace('border-t-2 border-slate-200', 'border-t border-slate-200')
content = content.replace('text-2xl font-bold uppercase tracking-widest text-slate-800 mb-8 border-b-2 border-slate-200 pb-4', 'text-sm font-bold uppercase tracking-widest text-slate-800 mb-6 border-b border-slate-200 pb-2')

# Fix massive font size on 'Closed-Loop Actions Today' metrics
content = content.replace('text-3xl font-bold text-teal-700', 'text-3xl font-bold tracking-tight text-teal-700')
content = content.replace('text-3xl font-bold text-emerald-600', 'text-3xl font-bold tracking-tight text-emerald-600')
content = content.replace('text-3xl font-bold text-amber-600', 'text-3xl font-bold tracking-tight text-amber-600')
content = content.replace('text-3xl font-bold text-slate-700', 'text-3xl font-bold tracking-tight text-slate-700')

with open('frontend/components/CommandCenter.tsx', 'w') as f:
    f.write(content)
