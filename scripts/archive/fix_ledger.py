with open('frontend/app/verified-ledger/page.tsx', 'r') as f:
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

# Fix Cards
content = content.replace('text-lg font-bold uppercase', 'text-xs font-semibold uppercase')
content = content.replace('text-xl font-bold text-slate-800', 'text-3xl font-bold text-slate-800')
content = content.replace('text-xl font-bold', 'text-3xl font-bold')

# Fix Table Headers
content = content.replace('border-b-4 border-slate-300', 'border-b border-slate-200')
content = content.replace('p-6 text-xs font-bold uppercase', 'p-4 text-xs font-semibold uppercase')

# Fix Table Rows
content = content.replace('divide-y-2 divide-slate-200', 'divide-y divide-slate-100')
content = content.replace('p-6 text-xl font-bold', 'p-4 text-sm font-bold')
content = content.replace('p-6 text-2xl font-bold', 'p-4 text-base font-bold')
content = content.replace('px-4 py-2 rounded-lg text-sm font-bold', 'px-2 py-1 rounded text-xs font-bold')
content = content.replace('p-6', 'p-4')
content = content.replace('p-12 text-center text-2xl', 'p-8 text-center text-sm')

with open('frontend/app/verified-ledger/page.tsx', 'w') as f:
    f.write(content)
