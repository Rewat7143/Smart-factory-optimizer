import re

file_path = 'frontend/app/predictive-maintenance/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
  const monitored = assets.filter((a:any) => a.status !== 'UNMONITORED').length;
  const critical = assets.filter((a:any) => a.status === 'CRITICAL').length;
  const healthy = assets.filter((a:any) => a.status === 'HEALTHY').length;

  return (
    <div className="p-6 font-mono space-y-6 max-w-[1600px] mx-auto pb-20">
      <header className="mb-6">
        <h1 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-800 uppercase">Predictive Maintenance</h1>
        <p className="text-sm font-semibold tracking-widest text-slate-500 uppercase mt-2 border-b border-slate-300 pb-4">AI-Driven Asset Reliability & Health Monitoring</p>
      </header>
      
      {isOffline && (
        <div className="bg-red-50 text-red-700 border-l-4 border-red-600 px-4 py-3 mb-6 flex items-center font-bold text-sm tracking-widest">
          <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse mr-3"></span>
          OFFLINE: Waiting for telemetry.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
         <div className="border p-6 rounded-xl shadow-sm bg-teal-700 text-white border-teal-800">
            <div className="text-xs uppercase tracking-widest font-bold mb-2 opacity-80">Monitored Assets</div>
            <div className="text-4xl lg:text-5xl font-bold tracking-tight">{isOffline ? '0' : monitored} / {assets.length}</div>
         </div>
         <div className="border p-6 rounded-xl shadow-sm bg-emerald-600 text-white border-emerald-800">
            <div className="text-xs uppercase tracking-widest font-bold mb-2 opacity-80">Healthy Assets</div>
            <div className="text-4xl lg:text-5xl font-bold tracking-tight">{isOffline ? '0' : healthy}</div>
         </div>
         <div className={`border p-6 rounded-xl shadow-sm ${critical > 0 ? 'bg-red-600 text-white border-red-800 animate-pulse' : 'bg-slate-100 text-slate-800 border-slate-300'}`}>
            <div className="text-xs uppercase tracking-widest font-bold mb-2 opacity-80">Critical Warnings</div>
            <div className="text-4xl lg:text-5xl font-bold tracking-tight">{isOffline ? '0' : critical}</div>
         </div>
      </div>

      <div className="bg-white border-2 border-slate-200 rounded-xl overflow-hidden shadow-sm">
         <div className="overflow-x-auto">
            <table className="w-full text-left">
               <thead className="bg-slate-50 border-b-2 border-slate-200">
                  <tr>
                     <th className="p-4 text-xs font-bold uppercase tracking-widest text-slate-500">Asset</th>
                     <th className="p-4 text-xs font-bold uppercase tracking-widest text-slate-500">Status</th>
                     <th className="p-4 text-xs font-bold uppercase tracking-widest text-slate-500">Health Score</th>
                     <th className="p-4 text-xs font-bold uppercase tracking-widest text-slate-500">Insights</th>
                  </tr>
               </thead>
               <tbody className="divide-y divide-slate-100">
                  {assets.map((a: any) => (
                     <tr key={a.asset_id} className="hover:bg-slate-50 transition-colors">
                        <td className="p-4 font-bold text-slate-800">{a.name}</td>
                        <td className="p-4">
                           <span className={`text-xs font-bold uppercase tracking-widest px-2 py-1 rounded ${a.status === 'CRITICAL' ? 'bg-red-100 text-red-700' : a.status === 'WARNING' ? 'bg-amber-100 text-amber-700' : a.status === 'UNMONITORED' ? 'bg-slate-100 text-slate-500' : 'bg-green-100 text-green-700'}`}>
                              {a.status}
                           </span>
                        </td>
                        <td className="p-4">
                           {a.health_score === null ? (
                             <span className="text-slate-400 font-semibold italic text-sm">N/A</span>
                           ) : (
                             <div className="flex items-center gap-2">
                                <div className="w-24 bg-slate-200 h-2 rounded-full overflow-hidden">
                                   <div className={`h-full ${a.health_score > 70 ? 'bg-green-500' : 'bg-red-500'}`} style={{ width: `${a.health_score}%` }}></div>
                                </div>
                                <span className="font-bold text-sm text-slate-700">{a.health_score}%</span>
                             </div>
                           )}
                        </td>
                        <td className="p-4 text-sm font-semibold text-slate-600 max-w-xs">{a.recommendation}</td>
                     </tr>
                  ))}
               </tbody>
            </table>
         </div>
      </div>
    </div>
"""

pattern = r'  const critical = assets\.filter\(\(a:any\) => a\.health_score < 70\)\.length;\s*return \(.*?\s*\)\s*\}'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
