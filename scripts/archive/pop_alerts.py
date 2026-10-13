with open('frontend/components/CommandCenter.tsx', 'r') as f:
    content = f.read()

# The optimization box has: className={`text-lg font-bold font-bold ${pipeline?.optimization?.actions?.length > 0 ? 'text-teal-500' : 'text-emerald-400'}`}
# Wait, scale_ui might have scaled text-sm to text-lg font-bold.
# Let's replace the bg-slate-900 (now bg-slate-800 from upgrade_ui? No, upgrade_ui replaced bg-white with bg-slate-900. The opt box was bg-slate-900, maybe it became something else).
# Actually, the user will be thrilled with the top status cards being massively bold blocks of solid color.

import re

# Let's find "bg-slate-900 text-white" and replace with "bg-slate-800 text-white border-l-8 border-teal-500"
content = content.replace('bg-slate-900 text-white rounded-lg', 'bg-slate-800 text-white rounded-xl border-l-8 border-teal-500')

with open('frontend/components/CommandCenter.tsx', 'w') as f:
    f.write(content)
