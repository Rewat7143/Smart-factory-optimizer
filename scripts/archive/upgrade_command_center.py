with open('frontend/components/CommandCenter.tsx', 'r') as f:
    content = f.read()

# Make the "Without Autopilot vs With Autopilot" table look like a financial ledger
content = content.replace(
    'bg-slate-800 text-white p-6 text-center', 
    'bg-slate-50 border-b border-slate-200 p-6 flex justify-between items-center'
)

content = content.replace(
    '<h2 className="text-3xl font-bold uppercase tracking-widest">Without Autopilot <span className="text-slate-400 mx-4">vs</span> With Autopilot</h2>',
    '''
    <div className="flex flex-col text-left">
       <h2 className="text-lg font-bold text-slate-800 tracking-tight">Comparative Ledger</h2>
       <span className="text-xs text-slate-500 font-mono">ID: AUTOPILOT-VERIFIED-{new Date().toISOString().split('T')[0]}</span>
    </div>
    <div className="flex items-center gap-6">
       <div className="flex items-center gap-2 text-sm font-semibold text-slate-500"><div className="w-2 h-2 bg-slate-300 rounded-full"></div> Baseline (Without AI)</div>
       <div className="flex items-center gap-2 text-sm font-semibold text-teal-700"><div className="w-2 h-2 bg-teal-600 rounded-full"></div> Optimized (With AI)</div>
    </div>
    '''
)

# Remove the red border from the "Rejected (Prot)" card, make it look professional
content = content.replace('border-l-8 border-l-red-600', '')
content = content.replace('text-red-600', 'text-slate-700')

with open('frontend/components/CommandCenter.tsx', 'w') as f:
    f.write(content)
