with open('frontend/app/energy-economics/page.tsx', 'r') as f:
    content = f.read()

# Fix HUGE table texts
content = content.replace('text-2xl font-bold text-slate-800', 'text-base font-bold text-slate-800')
content = content.replace('text-xl font-bold text-slate-800', 'text-base font-bold text-slate-800')
content = content.replace('text-lg font-bold text-slate-500', 'text-sm font-semibold text-slate-500')
content = content.replace('border-t-4 border-slate-200 pt-4', 'border-t border-slate-200 pt-3')
content = content.replace('text-xs font-bold uppercase tracking-widest text-slate-500 mb-8 border-b-2 border-slate-200 pb-4', 'text-sm font-bold uppercase tracking-widest text-slate-800 mb-6 border-b border-slate-200 pb-2')
content = content.replace('text-2xl font-bold text-slate-800 uppercase', 'text-sm font-bold text-slate-800 uppercase tracking-widest')
content = content.replace('border-2 border-slate-200 rounded-xl', 'border border-slate-200 rounded-xl')
content = content.replace('text-lg font-bold text-slate-600', 'text-sm font-semibold text-slate-600')

# Buzzword fix missed earlier maybe?
content = content.replace('Enable AI scheduling to recover', 'Enable Autopilot scheduling to recover')
content = content.replace('text-red-600 text-lg font-bold tracking-widest', 'text-red-600 text-sm font-bold tracking-widest')

# Add explicit x-axis label equivalence for horizontal bar chart (Rule 10)
# We can add an x-axis equivalent footer to the chart section
content = content.replace(
'''            <div className="space-y-8">''',
'''            <div className="space-y-6">'''
)
content = content.replace(
'''            <div className="mt-12 p-6 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between">''',
'''            <div className="flex justify-between items-center text-xs font-bold text-slate-400 border-t border-slate-200 pt-2 mt-6">
               <span>0%</span>
               <span className="tracking-widest uppercase">Energy Cost Breakdown (%)</span>
               <span>100%</span>
            </div>
            
            <div className="mt-8 p-6 bg-slate-50 border border-slate-200 rounded-xl flex flex-col md:flex-row items-center justify-between gap-4">'''
)

with open('frontend/app/energy-economics/page.tsx', 'w') as f:
    f.write(content)
