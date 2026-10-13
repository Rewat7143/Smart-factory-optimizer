import re

file_path = 'frontend/app/scale-simulator/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

pattern = r'<p className="text-base font-bold text-slate-800 uppercase tracking-widest font-bold mt-1">Modeled Projection — Based on current factory optimization performance</p>'

replacement = """<p className="text-base font-bold text-slate-800 uppercase tracking-widest font-bold mt-1">Modeled Projection — Based on current factory optimization performance</p>
            <div className="mt-2 text-xs font-semibold uppercase tracking-widest text-amber-600 border border-amber-300 bg-amber-50 px-2 py-1 rounded inline-block">HYPOTHETICAL PROJECTION: Does not enter live measured results</div>"""

content = content.replace(pattern, replacement)

with open(file_path, 'w') as f:
    f.write(content)
