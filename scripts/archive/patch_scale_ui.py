import re

file_path = 'frontend/app/scale-simulator/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

# Add a more prominent disclaimer at the top
replacement = """
      {/* HEADER */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-end border-b border-slate-300 pb-4">
        <div>
          <h1 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-800 uppercase">Fleet Impact Simulator</h1>
          <p className="text-sm font-semibold tracking-widest text-slate-500 uppercase mt-2">Project ROI & Sustainability impact at scale</p>
        </div>
        <div className="mt-4 lg:mt-0 px-4 py-2 bg-amber-100 text-amber-800 border-2 border-amber-300 rounded font-bold text-xs uppercase tracking-widest">
           HYPOTHETICAL PROJECTION ONLY
        </div>
      </div>
"""

pattern = r'\s*\{\/\* HEADER \*\/\}\s*<div className="flex justify-between items-end border-b border-slate-300 pb-4">\s*<div>\s*<h1 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-800 uppercase">Fleet Impact Simulator<\/h1>\s*<p className="text-sm font-semibold tracking-widest text-slate-500 uppercase mt-2">Project ROI \& Sustainability impact at scale<\/p>\s*<\/div>\s*<\/div>'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
