export default function PeakRadar({ pipeline, demoState }: { pipeline: any, demoState: any }) {
  const { current_demand, predicted_peak, safe_target, headroom, peak_risk } = pipeline.pipeline;
  const isHigh = peak_risk === 'HIGH';
  
  return (
    <div className={`rounded-xl shadow-sm border-2 overflow-hidden flex flex-col h-[500px] ${isHigh ? 'bg-red-50 border-red-200' : 'bg-white border-slate-200'}`}>
       <div className={`px-4 py-2 border-b flex justify-between items-center ${isHigh ? 'bg-red-100 border-red-200' : 'bg-slate-50 border-slate-200'}`}>
          <h3 className={`font-mono text-base font-bold font-bold uppercase tracking-widest ${isHigh ? 'text-red-800' : 'text-slate-800'}`}>Peak Risk Radar</h3>
          <span className={`px-2 py-0.5 rounded text-base font-bold font-bold uppercase tracking-widest ${isHigh ? 'bg-red-600 text-white text-slate-800 animate-pulse' : 'bg-green-100 text-green-700'}`}>
            {peak_risk} RISK
          </span>
       </div>
       <div className="flex-1 p-4 flex flex-col">
          <div className="grid grid-cols-2 gap-4 mb-8">
             <div className="bg-white p-4 rounded border-2 border-slate-200 shadow-sm text-center">
               <div className="text-base font-bold font-mono font-bold uppercase text-slate-800 mb-1">Live Demand</div>
               <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">{current_demand.toFixed(1)} <span className="text-lg font-bold">kW</span></div>
             </div>
             <div className="bg-white p-4 rounded border-2 border-slate-200 shadow-sm text-center">
               <div className="text-base font-bold font-mono font-bold uppercase text-slate-800 mb-1">15m Forecast</div>
               <div className={`text-xl lg:text-2xl font-bold font-bold ${isHigh ? 'text-red-600' : 'text-teal-700'}`}>{predicted_peak.toFixed(1)} <span className="text-lg font-bold">kW</span></div>
             </div>
             <div className="bg-white p-4 rounded border-2 border-slate-200 shadow-sm text-center">
               <div className="text-base font-bold font-mono font-bold uppercase text-slate-800 mb-1">Safe Limit</div>
               <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">{safe_target.toFixed(1)} <span className="text-lg font-bold">kW</span></div>
             </div>
             <div className="bg-white p-4 rounded border-2 border-slate-200 shadow-sm text-center">
               <div className="text-base font-bold font-mono font-bold uppercase text-slate-800 mb-1">Headroom</div>
               <div className={`text-xl lg:text-2xl font-bold font-bold ${headroom < 0 ? 'text-red-600' : 'text-green-600'}`}>{headroom.toFixed(1)} <span className="text-lg font-bold">kW</span></div>
             </div>
          </div>
          
          <div className="flex-1 border-2 border-slate-200 bg-white rounded p-4 relative">
             <div className="text-base font-bold font-mono font-bold uppercase text-slate-800 mb-4">Demand Trajectory</div>
             <div className="absolute top-1/2 left-0 w-full border-t-2 border-dashed border-red-300"></div>
             <div className="absolute top-1/2 right-2 -mt-4 text-base font-bold font-bold text-red-500 uppercase">Limit {safe_target}kW</div>
             
             {/* Fake graph just for visual indication of trajectory relative to safe target */}
             <div className="absolute bottom-4 left-4 right-20 h-32 flex items-end justify-between px-2">
                {[1,2,3,4,5,6].map(i => {
                   let h = 20 + i*5;
                   if (isHigh && i > 4) h = 80 + (i-4)*15;
                   return (
                     <div key={i} className={`w-8 rounded-t transition-all duration-1000 ${isHigh && i>4 ? 'bg-red-400' : 'bg-slate-300'}`} style={{height: `${h}%`}}></div>
                   )
                })}
             </div>
          </div>

          {isHigh && (
            <div className="mt-4 bg-red-50 border-2 border-red-200 p-5 rounded text-lg font-bold text-red-800 font-medium">
               <strong>ROOT CAUSE IDENTIFIED:</strong> Flexible load overlap (Compressor + Pump) driving demand above threshold.
            </div>
          )}
       </div>
    </div>
  )
}
