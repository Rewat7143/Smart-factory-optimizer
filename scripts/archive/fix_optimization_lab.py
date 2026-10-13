import re

with open('frontend/app/optimization-lab/page.tsx', 'r') as f:
    content = f.read()

# Replace the entire return statement
return_block = re.search(r'return \(\n      <div.*$', content, re.DOTALL).group(0)

new_ui = '''return (
      <div className="max-w-[1600px] mx-auto space-y-6 font-mono text-slate-800 pb-20 p-6">
        
        {/* HEADER */}
        <div className="flex justify-between items-end border-b border-slate-300 pb-4">
          <div>
            <h1 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-800 uppercase">Optimization Engine</h1>
            <p className="text-sm font-semibold tracking-widest text-slate-500 uppercase mt-2">Production-Constrained AI Scheduler</p>
          </div>
          <div className="text-right">
             <div className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-1">Engine Status</div>
             <div className="flex items-center justify-end gap-2 text-teal-700 text-sm font-bold tracking-widest">
                <div className="w-2 h-2 rounded-full bg-teal-600 animate-pulse"></div> CLOSED-LOOP ACTIVE
             </div>
          </div>
        </div>

        {/* MAIN VISUAL */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
           <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col">
              <div className="text-sm font-bold uppercase tracking-widest text-slate-800 mb-1">OPTIMIZATION IMPACT — BEFORE vs AFTER</div>
              <div className="text-xs font-semibold text-slate-500 mb-6 border-b border-slate-100 pb-2">Direct consequence of the latest scheduled AI intervention.</div>
              
              {!pipeline?.optimization || pipeline.optimization.status !== 'OPTIMIZED' ? (
                 <div className="flex-1 flex items-center justify-center text-slate-400 font-bold tracking-widest">NO ACTIVE OPTIMIZATION REQUIRED</div>
              ) : (
                 <div className="flex-1 flex flex-col justify-center space-y-8">
                    {pipeline.optimization.actions.map((act: any, idx: number) => (
                       <div key={idx} className="bg-slate-50 border border-slate-200 rounded-xl p-6 flex flex-col md:flex-row items-center gap-6">
                          <div className="flex-1 text-center">
                             <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Predicted Peak (Without AI)</div>
                             <div className="text-4xl font-bold text-slate-800 line-through decoration-red-500 decoration-4 opacity-70">{pipeline.pipeline.predicted_peak.toFixed(1)} kW</div>
                          </div>
                          
                          <div className="flex-1 text-center bg-teal-50 border border-teal-200 p-4 rounded-lg">
                             <div className="text-xs font-bold text-teal-700 uppercase tracking-widest mb-2">Action Executed</div>
                             <div className="text-sm font-bold text-teal-900">{act.action}</div>
                          </div>
                          
                          <div className="flex-1 text-center">
                             <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Optimized Peak (With AI)</div>
                             <div className="text-4xl font-bold text-teal-700">{pipeline.pipeline.safe_target.toFixed(1)} kW</div>
                          </div>
                       </div>
                    ))}
                    
                    <div className="grid grid-cols-3 gap-4 text-center">
                       <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-lg">
                          <div className="text-xs font-bold text-emerald-700 uppercase tracking-widest mb-1">Peak Avoided</div>
                          <div className="text-2xl font-bold text-emerald-800">{(pipeline.pipeline.predicted_peak - pipeline.pipeline.safe_target).toFixed(1)} kW</div>
                       </div>
                       <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-lg">
                          <div className="text-xs font-bold text-emerald-700 uppercase tracking-widest mb-1">Cost Avoided</div>
                          <div className="text-2xl font-bold text-emerald-800">₹{Math.round((pipeline.pipeline.predicted_peak - pipeline.pipeline.safe_target) * 350)}</div>
                       </div>
                       <div className="bg-slate-50 border border-slate-200 p-4 rounded-lg">
                          <div className="text-xs font-bold text-slate-600 uppercase tracking-widest mb-1">Production Impact</div>
                          <div className="text-2xl font-bold text-slate-800">0%</div>
                       </div>
                    </div>
                 </div>
              )}
           </div>

           <div className="lg:col-span-1 space-y-6">
              {/* ASSET CONSTRAINTS */}
              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                 <div className="text-sm font-bold uppercase tracking-widest text-slate-800 mb-1">Asset Constraints Matrix</div>
                 <div className="text-xs font-semibold text-slate-500 mb-6 border-b border-slate-100 pb-2">AI scheduling boundaries determined by production targets.</div>
                 
                 <div className="space-y-4">
                     {(pipeline?.attribution || []).slice(0, 5).map((attr: any, i: number) => (
                        <div key={i} className="flex justify-between items-center text-sm font-bold">
                           <span className="text-slate-700">{attr.name}</span>
                           <span className="flex gap-4">
                              <span className={`px-2 py-1 rounded text-xs tracking-widest ${attr.type === 'CRITICAL' ? 'bg-red-100 text-red-700' : 'bg-teal-100 text-teal-700'}`}>
                                 {attr.type === 'CRITICAL' ? 'PROTECTED' : 'FLEXIBLE'}
                              </span>
                           </span>
                        </div>
                     ))}
                 </div>
              </div>
           </div>
        </div>

        <div className="mt-8 border-t border-slate-200 pt-6 flex justify-between items-center text-xs text-slate-500 font-semibold">
           <div>Report Generated by Factory Energy Autopilot Engine</div>
           <div>Data Source: {pipeline ? 'LIVE MODBUS RTU' : 'OFFLINE'}</div>
           <div>{new Date().toISOString().replace('T', ' ').substring(0, 19)} UTC</div>
        </div>
      </div>
  )
}'''

content = content.replace(return_block, new_ui)

with open('frontend/app/optimization-lab/page.tsx', 'w') as f:
    f.write(content)
