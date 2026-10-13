import re

def patch():
    with open('frontend/components/CommandCenter.tsx', 'r') as f:
        content = f.read()

    replacement = """                  <div className={`text-sm font-bold ${pipeline?.optimization?.actions?.length > 0 ? 'text-blue-400' : 'text-green-400'}`}>
                     {pipeline?.optimization?.actions?.length > 0 
                        ? pipeline.optimization.actions[0].action 
                        : (pipeline?.optimization?.message || 'No action required. Limits safe.')}
                  </div>
                  
                  {pipeline?.optimization?.actions?.length > 0 && pipeline.optimization.actions[0].why && (
                     <div className="mt-4 pt-4 border-t border-slate-700">
                        <div className="text-[9px] text-amber-400 uppercase font-bold tracking-widest mb-2 flex items-center gap-1">
                           <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                           WHY? ENGINEERING EXPLANATION
                        </div>
                        <div className="space-y-1 mb-3">
                           {pipeline.optimization.actions[0].why.reasons.map((r: string, i: number) => (
                              <div key={i} className="flex gap-2 text-[10px] text-slate-300">
                                 <span className="text-slate-500">•</span> {r}
                              </div>
                           ))}
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-[9px] uppercase font-bold tracking-widest">
                           <div className="bg-slate-800 p-2 rounded border border-slate-700">
                              <div className="text-slate-500 mb-0.5">Protected Asset</div>
                              <div className="text-blue-400">{pipeline.optimization.actions[0].why.protected}</div>
                           </div>
                           <div className="bg-slate-800 p-2 rounded border border-slate-700">
                              <div className="text-slate-500 mb-0.5">Flexible Asset</div>
                              <div className="text-green-400">{pipeline.optimization.actions[0].why.flexible}</div>
                           </div>
                        </div>
                     </div>
                  )}
"""
    
    # We want to replace the single closing div of the recommended action with our block that adds the WHY underneath it
    search_str = """                  <div className={`text-sm font-bold ${pipeline?.optimization?.actions?.length > 0 ? 'text-blue-400' : 'text-green-400'}`}>
                     {pipeline?.optimization?.actions?.length > 0 
                        ? pipeline.optimization.actions[0].action 
                        : (pipeline?.optimization?.message || 'No action required. Limits safe.')}
                  </div>"""
    
    if search_str in content:
        content = content.replace(search_str, replacement)
        with open('frontend/components/CommandCenter.tsx', 'w') as f:
            f.write(content)
        print("Patched WHY")
    else:
        print("Could not find WHY target string")

patch()
