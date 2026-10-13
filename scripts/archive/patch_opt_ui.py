import re

file_path = 'frontend/app/optimization-lab/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
              {!pipeline?.optimization?.actions?.length ? (
                 <div className="flex-1 flex items-center justify-center text-slate-400 font-bold tracking-widest">
                   {pipeline?.optimization?.status === 'NORMAL' ? 'NO ACTIVE OPTIMIZATION REQUIRED' : (pipeline?.optimization?.message || 'NO ACTIVE OPTIMIZATION REQUIRED')}
                 </div>
"""

pattern = r'\{\!pipeline\?\.optimization \|\| pipeline\.optimization\.status \!\=\= \'OPTIMIZED\' \? \(\s*<div className="flex-1 flex items-center justify-center text-slate-400 font-bold tracking-widest">NO ACTIVE OPTIMIZATION REQUIRED<\/div>\s*\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
