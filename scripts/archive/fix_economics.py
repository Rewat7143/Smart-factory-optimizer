with open('frontend/app/energy-economics/page.tsx', 'r') as f:
    content = f.read()

# Fix Header
content = content.replace(
    '<h1 className="text-xl lg:text-2xl font-bold tracking-tight text-slate-800 uppercase">', 
    '<h1 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-800 uppercase">'
)
content = content.replace(
    '<p className="text-lg lg:text-xl font-bold tracking-widest text-slate-800 uppercase mt-2">', 
    '<p className="text-sm font-semibold tracking-widest text-slate-500 uppercase mt-2">'
)
content = content.replace(
    'border-b-4 border-slate-300 pb-6', 
    'border-b border-slate-300 pb-4'
)

# Fix primary metrics
content = content.replace('text-xl font-bold uppercase tracking-widest text-slate-300', 'text-sm font-semibold uppercase tracking-widest text-slate-400')
content = content.replace('text-xl font-bold uppercase tracking-widest text-slate-500', 'text-sm font-semibold uppercase tracking-widest text-slate-500')
content = content.replace('text-2xl font-bold tracking-tight mb-2', 'text-5xl font-bold tracking-tight mb-2')
content = content.replace('text-2xl font-bold tracking-tight text-slate-800 mb-2', 'text-5xl font-bold tracking-tight text-slate-800 mb-2')

# Fix secondary metrics
content = content.replace('text-2xl font-bold tracking-tight text-slate-800', 'text-lg font-bold tracking-tight text-slate-800')

with open('frontend/app/energy-economics/page.tsx', 'w') as f:
    f.write(content)
