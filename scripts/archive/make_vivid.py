with open('frontend/components/CommandCenter.tsx', 'r') as f:
    content = f.read()

import re

# We will replace the colorMap in StatusCard
old_color_map = """
  const colorMap = {
     blue: 'border-teal-200 bg-teal-50 text-teal-900',
     purple: 'border-purple-200 bg-purple-50 text-purple-900',
     red: 'border-red-200 bg-red-50 text-red-900',
     green: 'border-emerald-200 bg-emerald-50 text-emerald-900',
     slate: 'border-slate-200 bg-white text-slate-800',
     teal: 'border-teal-200 bg-teal-50 text-teal-900'
  }
"""

# Wait, `scale_ui.py` might have replaced `bg-white` with something else or scaled it. Let's just find the `colorMap = {` block
color_map_pattern = re.compile(r"const colorMap = \{[\s\S]*?\}", re.MULTILINE)

new_color_map = """const colorMap: Record<string, string> = {
     blue: 'border-teal-800 bg-teal-700 text-white shadow-teal-700/50',
     purple: 'border-indigo-800 bg-indigo-700 text-white shadow-indigo-700/50',
     red: 'border-red-800 bg-red-600 text-white shadow-red-600/50 animate-pulse',
     green: 'border-emerald-800 bg-emerald-600 text-white shadow-emerald-600/50',
     slate: 'border-slate-800 bg-slate-700 text-white shadow-slate-700/50',
     teal: 'border-teal-800 bg-teal-600 text-white shadow-teal-600/50'
  }"""

content = color_map_pattern.sub(new_color_map, content)

# Also scale the StatusCard HTML
card_html = """
  return (
     <div className={`border-4 p-8 rounded-2xl shadow-xl ${colorMap[color]}`}>
        <div className="text-sm uppercase tracking-widest font-black opacity-90 mb-2">{title}</div>
        <div className="text-5xl font-black tracking-tighter">{value}</div>
     </div>
  )
"""
# The old HTML looks something like:
card_pattern = re.compile(r"return \(\s*<div className=\{\`border-2 p-6.*?</div>\s*\)\s*\}", re.DOTALL)
if card_pattern.search(content):
    content = card_pattern.sub(card_html + "\n}", content)
else:
    # try the original one
    orig_card_pattern = re.compile(r"return \(\s*<div className=\{\`border p-4.*?</div>\s*\)\s*\}", re.DOTALL)
    content = orig_card_pattern.sub(card_html + "\n}", content)

with open('frontend/components/CommandCenter.tsx', 'w') as f:
    f.write(content)
