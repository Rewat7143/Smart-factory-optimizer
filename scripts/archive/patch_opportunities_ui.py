import re

file_path = 'frontend/app/opportunities/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
                  <div>
                    <div className="text-base font-bold font-semibold text-slate-800 uppercase tracking-wider mb-2">Recommendation & Constraints</div>
                    <p className="text-slate-800 text-lg font-bold bg-slate-50 p-5 rounded border-2 border-slate-100 mb-2">{opp.recommended_action}</p>
                    <div className="flex gap-4 text-sm mt-3">
                        <div className="bg-slate-50 border border-slate-200 px-3 py-2 rounded">
                            <span className="font-bold text-slate-500 uppercase text-[10px] block mb-1">Expected Change</span>
                            <span className="font-bold text-slate-800">{opp.expected_kw_change || '-'}</span>
                        </div>
                        <div className="bg-slate-50 border border-slate-200 px-3 py-2 rounded">
                            <span className="font-bold text-slate-500 uppercase text-[10px] block mb-1">Financial Impact</span>
                            <span className="font-bold text-emerald-600">{opp.potential_monthly_inr || '-'}</span>
                        </div>
                        <div className="bg-slate-50 border border-slate-200 px-3 py-2 rounded flex-1">
                            <span className="font-bold text-slate-500 uppercase text-[10px] block mb-1">Production Constraint</span>
                            <span className="font-semibold text-slate-600">{opp.production_constraint || 'None'}</span>
                        </div>
                    </div>
                  </div>
"""

pattern = r'<div>\s*<div className="text-base font-bold font-semibold text-slate-800 uppercase tracking-wider mb-2">Recommendation</div>\s*<p className="text-slate-800 text-lg font-bold bg-slate-50 p-5 rounded border-2 border-slate-100">{opp\.recommended_action}</p>\s*</div>'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
