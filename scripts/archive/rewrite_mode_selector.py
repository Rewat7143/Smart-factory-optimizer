with open('frontend/components/GlobalHeader.tsx', 'r') as f:
    content = f.read()

import re
old_toggle = re.search(r'\{\/\* Toggle Switch \*\/\}.*?<\/div>\n\n        <SystemStatus', content, re.DOTALL)
if old_toggle:
    new_toggle = '''{/* Toggle Switch */}
        <div className="flex flex-col border border-slate-300 rounded overflow-hidden bg-slate-100 shadow-inner">
           <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 bg-slate-200 px-2 py-0.5 border-b border-slate-300">Operating Mode</div>
           <div className="flex">
               <button 
                 onClick={() => setMode('SIMULATION')}
                 className={`flex items-center gap-2 px-3 py-1.5 text-xs font-bold uppercase tracking-widest transition-all ${mode === 'SIMULATION' ? 'bg-white text-slate-800 shadow-sm border-r border-slate-200' : 'text-slate-500 hover:text-slate-800 border-r border-slate-200 opacity-70'}`}
               >
                  <div className={`w-2 h-2 rounded-full border border-slate-400 flex items-center justify-center`}><div className={`w-1 h-1 rounded-full ${mode === 'SIMULATION' ? 'bg-teal-600' : 'bg-transparent'}`}></div></div>
                  SIMULATION
               </button>
               <button 
                 onClick={() => setMode('LIVE')}
                 className={`flex items-center gap-2 px-3 py-1.5 text-xs font-bold uppercase tracking-widest transition-all ${mode === 'LIVE' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-800 opacity-70'}`}
               >
                  <div className={`w-2 h-2 rounded-full border border-slate-400 flex items-center justify-center`}><div className={`w-1 h-1 rounded-full ${mode === 'LIVE' ? 'bg-red-600 animate-pulse' : 'bg-transparent'}`}></div></div>
                  LIVE FACTORY
               </button>
           </div>
        </div>

        <SystemStatus'''
    content = content.replace(old_toggle.group(0), new_toggle)
    with open('frontend/components/GlobalHeader.tsx', 'w') as f:
        f.write(content)
