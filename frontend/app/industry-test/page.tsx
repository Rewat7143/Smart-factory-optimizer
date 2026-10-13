"use client"

export default function IndustryTestCenter() {
  return (
    <div className="max-w-6xl mx-auto space-y-6 font-mono">
       <div className="bg-white text-slate-800 p-4 rounded-xl border-2 border-slate-200 shadow flex justify-between items-center">
          <div>
             <h1 className="text-xl lg:text-2xl font-bold font-bold uppercase tracking-widest text-teal-500">Industry Connect Workflow</h1>
             <p className="text-lg font-bold text-slate-800 mt-1">Real-world telemetry integration and model deployment center.</p>
          </div>
          <button className="bg-teal-700 text-white hover:bg-teal-500 px-6 py-3 rounded text-lg font-bold font-bold uppercase tracking-widest shadow">
             Initialize Gateway
          </button>
       </div>

       <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow-sm border-2 border-slate-200 p-4 flex flex-col items-center justify-center text-center">
             <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
             </div>
             <div className="font-bold text-slate-700 uppercase tracking-widest mb-1">Arduino UNO Q</div>
             <div className="text-lg font-bold text-slate-800">Edge Gateway Connected</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border-2 border-slate-200 p-4 flex flex-col items-center justify-center text-center">
             <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
             </div>
             <div className="font-bold text-slate-700 uppercase tracking-widest mb-1">Main Meter (Modbus)</div>
             <div className="text-lg font-bold text-slate-800">Polling at 1Hz</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border-2 border-slate-200 p-4 flex flex-col items-center justify-center text-center">
             <div className="w-16 h-16 bg-blue-100 text-teal-700 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>
             </div>
             <div className="font-bold text-slate-700 uppercase tracking-widest mb-1">Telemetry DB</div>
             <div className="text-lg font-bold text-slate-800">Latency: 14ms</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border-2 border-slate-200 p-4 flex flex-col items-center justify-center text-center">
             <div className="w-16 h-16 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
             </div>
             <div className="font-bold text-slate-700 uppercase tracking-widest mb-1">AI Pipeline</div>
             <div className="text-lg font-bold text-slate-800">Inference Ready</div>
          </div>
       </div>

       <div className="bg-white rounded-xl shadow-sm border-2 border-slate-200 p-5">
          <h2 className="text-lg font-bold text-slate-800 uppercase tracking-widest mb-8">Deployment Workflow</h2>
          
          <div className="relative">
             <div className="absolute top-0 bottom-0 left-6 w-1 bg-slate-200"></div>
             
             {[
                { step: 1, name: 'CONNECT EDGE HARDWARE', status: 'COMPLETE', desc: 'Arduino UNO Q established secure MQTT connection to Cloud.' },
                { step: 2, name: 'VERIFY TELEMETRY', status: 'COMPLETE', desc: 'Modbus TCP parsing successful. Data quality 99.9%.' },
                { step: 3, name: 'COLLECT BASELINE', status: 'COMPLETE', desc: '14 days of historical factory load profile recorded.' },
                { step: 4, name: 'TRAIN XGBOOST FORECAST', status: 'COMPLETE', desc: 'Model trained on 20,160 samples. Validated MAE 1.2 kW.' },
                { step: 5, name: 'START LIVE INFERENCE', status: 'ACTIVE', desc: 'Engine predicting 15-minute rolling peak demand.' },
                { step: 6, name: 'ACTIVATE OPTIMIZER', status: 'READY', desc: 'OR-Tools CP-SAT solver ready for counterfactual generation.' }
             ].map((s, i) => (
                <div key={i} className="relative flex items-start gap-5 mb-8 last:mb-0">
                   <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-slate-800 z-10 ${s.status === 'COMPLETE' ? 'bg-green-500' : s.status === 'ACTIVE' ? 'bg-teal-700 text-white animate-pulse' : 'bg-slate-300'}`}>
                      {s.step}
                   </div>
                   <div className="pt-2">
                      <div className="flex items-center gap-4 mb-1">
                         <h3 className="font-bold text-slate-800 uppercase tracking-wider">{s.name}</h3>
                         <span className={`px-2 py-0.5 rounded text-base font-bold font-bold uppercase tracking-widest ${
                            s.status === 'COMPLETE' ? 'bg-green-100 text-green-700' :
                            s.status === 'ACTIVE' ? 'bg-blue-100 text-blue-700' :
                            'bg-slate-50 text-slate-800'
                         }`}>{s.status}</span>
                      </div>
                      <p className="text-slate-800 text-lg font-bold">{s.desc}</p>
                   </div>
                </div>
             ))}
          </div>
       </div>
    </div>
  )
}
