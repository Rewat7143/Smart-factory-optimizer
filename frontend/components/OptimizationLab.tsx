export default function OptimizationLab({ pipeline, setSimulatedAction, simulatedAction }: { pipeline: any, setSimulatedAction: any, simulatedAction: boolean }) {
  const opt = pipeline.optimization;
  const isHigh = pipeline.pipeline.peak_risk === 'HIGH';

  if (!isHigh || opt.status !== 'OPTIMIZED') {
     return (
        <div className="bg-white rounded-xl shadow-sm border-2 border-slate-200 overflow-hidden flex flex-col h-[600px]">
           <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
              <h3 className="font-mono text-base font-bold font-bold text-slate-800 uppercase tracking-widest">Optimization Lab</h3>
           </div>
           <div className="flex-1 flex items-center justify-center text-slate-800 font-mono text-base font-bold">
              WAITING FOR ANOMALY TRIGGER
           </div>
        </div>
     )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border-2 border-blue-300 overflow-hidden flex flex-col h-[600px]">
       <div className="bg-teal-50 px-4 py-3 border-b border-teal-200 flex justify-between items-center">
          <h3 className="font-mono text-base font-bold font-bold text-teal-900 uppercase tracking-widest">Optimization Lab</h3>
       </div>
       
       <div className="flex-1 p-4 overflow-y-auto font-mono">
          <table className="w-full text-left border-collapse text-base font-bold mb-8">
             <thead>
                <tr className="border-b-2 border-slate-200 text-slate-800">
                   <th className="pb-2 font-bold uppercase tracking-wider">Candidate Option</th>
                   <th className="pb-2 font-bold uppercase tracking-wider text-right">Peak</th>
                   <th className="pb-2 font-bold uppercase tracking-wider text-right">Prod</th>
                   <th className="pb-2 font-bold uppercase tracking-wider text-right">Status</th>
                </tr>
             </thead>
             <tbody>
                {opt.alternatives.map((alt: any, idx: number) => {
                   if (alt.status === 'CURRENT' || alt.status === 'ALTERNATIVE') return null;
                   const isSel = alt.status === 'SELECTED';
                   return (
                     <tr key={idx} className={`border-b border-slate-100 ${isSel ? 'bg-green-50' : 'bg-red-50'}`}>
                        <td className="py-3 px-2 font-semibold text-slate-800">
                           {alt.name}
                           <div className={`text-lg font-bold font-bold mt-1 ${isSel ? 'text-green-600' : 'text-red-500'}`}>{alt.reason || (isSel ? 'Valid safe schedule' : 'Constraint violation')}</div>
                        </td>
                        <td className="py-3 px-2 text-right font-bold text-slate-700">{alt.peak} kW</td>
                        <td className="py-3 px-2 text-right font-bold text-slate-700">{alt.production}</td>
                        <td className="py-3 px-2 text-right">
                           <span className={`px-2 py-1 rounded text-lg font-bold font-bold font-bold uppercase tracking-widest ${isSel ? 'bg-green-600 text-slate-800' : 'bg-red-200 text-red-800'}`}>
                              {alt.status}
                           </span>
                        </td>
                     </tr>
                   )
                })}
             </tbody>
          </table>

          <div className="bg-white rounded-lg p-5 text-slate-800 mb-6 shadow-inner">
             <div className="text-base font-bold text-slate-800 font-bold uppercase tracking-widest mb-4">Consequence Engine</div>
             
             <div className="grid grid-cols-2 gap-5 text-lg font-bold">
                <div>
                   <div className="text-red-400 font-bold mb-2 uppercase text-base font-bold tracking-wider border-b border-slate-200 pb-1">If You Do Nothing</div>
                   <div className="space-y-1 mt-3">
                      <div className="flex justify-between"><span className="text-slate-800">Peak:</span> <span className="font-bold">{pipeline.pipeline.predicted_peak.toFixed(1)} kW</span></div>
                      <div className="flex justify-between"><span className="text-slate-800">Risk:</span> <span className="text-red-400 font-bold">HIGH</span></div>
                      <div className="flex justify-between"><span className="text-slate-800">Penalty:</span> <span className="text-red-400 font-bold">Likely</span></div>
                   </div>
                </div>
                <div>
                   <div className="text-green-400 font-bold mb-2 uppercase text-base font-bold tracking-wider border-b border-slate-200 pb-1">With Optimization</div>
                   <div className="space-y-1 mt-3">
                      <div className="flex justify-between"><span className="text-slate-800">Peak:</span> <span className="font-bold">{(pipeline.pipeline.predicted_peak - 28.5).toFixed(1)} kW</span></div>
                      <div className="flex justify-between"><span className="text-slate-800">Risk:</span> <span className="text-green-400 font-bold">LOW</span></div>
                      <div className="flex justify-between"><span className="text-slate-800">Prod:</span> <span className="font-bold">100%</span></div>
                   </div>
                </div>
             </div>
          </div>

          <button 
             onClick={() => setSimulatedAction(!simulatedAction)}
             className={`w-full py-4 rounded-lg font-bold uppercase tracking-widest shadow transition-colors flex flex-col items-center justify-center ${
                simulatedAction ? 'bg-green-600 hover:bg-green-700 text-slate-800' : 'bg-teal-700 text-white hover:bg-blue-700 text-slate-800'
             }`}
          >
             <span>{simulatedAction ? 'Simulation Applied - Click to Revert' : 'Apply Schedule In Simulation'}</span>
          </button>
       </div>
    </div>
  )
}
