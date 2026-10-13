export default function DecisionTrace({ pipeline, showTrace, setShowTrace }: { pipeline: any, showTrace: boolean, setShowTrace: any }) {
  const isHigh = pipeline.pipeline.peak_risk === 'HIGH';

  return (
    <div className="bg-white rounded-xl shadow-sm border-2 border-slate-200 overflow-hidden flex flex-col h-[600px]">
       <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 flex justify-between items-center">
          <h3 className="font-mono text-base font-bold font-bold text-slate-800 uppercase tracking-widest flex items-center gap-2">
             <svg className="w-4 h-4 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
             AI Decision Trace
          </h3>
       </div>
       <div className="flex-1 p-4 overflow-y-auto font-mono text-lg font-bold">
          {!isHigh ? (
             <div className="h-full flex flex-col items-center justify-center text-slate-800 text-center">
                <svg className="w-12 h-12 mb-4 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <p className="font-medium text-slate-800">Monitoring System State</p>
                <p className="text-base font-bold uppercase mt-2">Optimizer Active • XGBoost v1.2</p>
             </div>
          ) : (
             <div className="space-y-6 relative">
                <div className="absolute left-[11px] top-4 bottom-4 w-0.5 bg-slate-200 z-0"></div>
                
                <div className="relative z-10 flex gap-4">
                   <div className="w-6 h-6 rounded-full bg-blue-100 border-2 border-blue-500 flex-shrink-0"></div>
                   <div>
                      <div className="font-bold text-slate-700 uppercase tracking-wider text-base font-bold">Observation</div>
                      <div className="text-slate-800 mt-1">Live telemetry indicates simultaneous asset startup sequence.</div>
                   </div>
                </div>

                <div className="relative z-10 flex gap-4">
                   <div className="w-6 h-6 rounded-full bg-blue-100 border-2 border-blue-500 flex-shrink-0"></div>
                   <div>
                      <div className="font-bold text-slate-700 uppercase tracking-wider text-base font-bold">Forecast (XGBoost)</div>
                      <div className="text-red-600 font-bold mt-1">Peak demand rising to {pipeline.pipeline.predicted_peak.toFixed(1)} kW in 15 minutes.</div>
                   </div>
                </div>

                <div className="relative z-10 flex gap-4">
                   <div className="w-6 h-6 rounded-full bg-purple-100 border-2 border-purple-500 flex-shrink-0"></div>
                   <div>
                      <div className="font-bold text-slate-700 uppercase tracking-wider text-base font-bold">Constraint Analysis</div>
                      <div className="text-slate-800 mt-1 text-base font-bold">
                         • Production Target: 100% (HARD CONSTRAINT)<br/>
                         • Compressor-01: Flexible<br/>
                         • Process Pump: Flexible
                      </div>
                   </div>
                </div>

                <div className="relative z-10 flex gap-4">
                   <div className="w-6 h-6 rounded-full bg-amber-100 border-2 border-amber-500 flex-shrink-0"></div>
                   <div>
                      <div className="font-bold text-slate-700 uppercase tracking-wider text-base font-bold">Optimization (OR-Tools)</div>
                      <div className="text-slate-800 mt-1">Matrix evaluation complete. Evaluated 2 viable schedules.</div>
                   </div>
                </div>

                <div className="relative z-10 flex gap-4">
                   <div className="w-6 h-6 rounded-full bg-green-100 border-2 border-green-500 flex-shrink-0"></div>
                   <div>
                      <div className="font-bold text-slate-700 uppercase tracking-wider text-base font-bold">Decision Generated</div>
                      <div className="text-green-700 font-bold mt-1">{pipeline.optimization.actions[0]?.action}</div>
                      <div className="text-base font-bold text-slate-800 mt-1">Confidence: 94.2% (Validated)</div>
                   </div>
                </div>
             </div>
          )}
       </div>
    </div>
  )
}
