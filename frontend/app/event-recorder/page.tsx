"use client"
import { useState, useEffect } from 'react'

export default function EventRecorder() {
  const [pipeline, setPipeline] = useState<any>(null)
  const [demoState, setDemoState] = useState<any>(null)
  
  useEffect(() => {
    const fetchState = async () => {
      try {
        const demoRes = await fetch(`${(typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))}/simulation/state`)
        const optRes = await fetch(`${(typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))}/optimize`, { method: 'POST' })
        if (demoRes.ok) setDemoState(await demoRes.json())
        if (optRes.ok) setPipeline(await optRes.json())
      } catch (e) {}
    }
    fetchState()
    let isMounted = true; let tid: any; const loop = async () => { if (!isMounted) return; await fetchState(); if(isMounted) tid = setTimeout(loop, 1500); }; loop(); return () => { isMounted = false; clearTimeout(tid); }
    
  }, [])

  return (
    <div className="space-y-6 max-w-5xl mx-auto font-mono">
       <div className="bg-white text-slate-800 p-4 rounded-xl border-2 border-slate-200 shadow flex justify-between items-center">
          <div>
             <h1 className="text-xl lg:text-2xl font-bold font-bold uppercase tracking-widest">Energy Flight Recorder</h1>
             <p className="text-lg font-bold text-slate-800 mt-1">Immutable log of factory energy events, anomalies, and AI decisions.</p>
          </div>
          <div className="flex gap-4">
             <button className="bg-teal-700 text-white hover:bg-teal-500 px-4 py-2 rounded text-base font-bold font-bold uppercase tracking-widest shadow flex items-center gap-2">
                <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span> Live Monitoring
             </button>
             <button className="bg-slate-50 hover:bg-slate-700 px-4 py-2 rounded border-2 border-slate-600 text-base font-bold font-bold uppercase tracking-widest shadow">
                Replay Event #003
             </button>
          </div>
       </div>

       <div className="bg-white rounded-xl shadow-sm border-2 border-slate-200 overflow-hidden">
          <table className="w-full text-left text-lg font-bold">
             <thead className="bg-slate-50 border-b border-slate-200 text-base font-bold text-slate-800 uppercase tracking-widest">
                <tr>
                   <th className="p-4">Timestamp</th>
                   <th className="p-4">Category</th>
                   <th className="p-4">Event Description</th>
                   <th className="p-4">Severity</th>
                   <th className="p-4">Status</th>
                </tr>
             </thead>
             <tbody className="divide-y divide-slate-100">
                <tr className="hover:bg-slate-50">
                   <td className="p-4 text-slate-800">16:21:35</td>
                   <td className="p-4 font-bold text-slate-700">HUMAN ACTION</td>
                   <td className="p-4">Operator acknowledged optimization recommendation.</td>
                   <td className="p-4"><span className="px-2 py-1 bg-slate-50 text-slate-800 rounded text-base font-bold font-bold">INFO</span></td>
                   <td className="p-4"><span className="text-green-600 font-bold">RECORDED</span></td>
                </tr>
                <tr className="hover:bg-slate-50 bg-green-50/30">
                   <td className="p-4 text-slate-800">16:21:27</td>
                   <td className="p-4 font-bold text-slate-700">AI OPTIMIZER</td>
                   <td className="p-4">Generated schedule: Delay Compressor-01 by 10 minutes.</td>
                   <td className="p-4"><span className="px-2 py-1 bg-green-100 text-green-700 rounded text-base font-bold font-bold">DECISION</span></td>
                   <td className="p-4"><span className="text-green-600 font-bold">GENERATED</span></td>
                </tr>
                <tr className="hover:bg-slate-50">
                   <td className="p-4 text-slate-800">16:21:24</td>
                   <td className="p-4 font-bold text-slate-700">AI ANALYZER</td>
                   <td className="p-4">Root cause identified: Compressor + Pump overlap during production.</td>
                   <td className="p-4"><span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-base font-bold font-bold">ANALYSIS</span></td>
                   <td className="p-4"><span className="text-green-600 font-bold">COMPLETE</span></td>
                </tr>
                <tr className="hover:bg-slate-50 bg-red-50/30">
                   <td className="p-4 text-slate-800">16:21:23</td>
                   <td className="p-4 font-bold text-slate-700">SYSTEM ALARM</td>
                   <td className="p-4 text-red-600 font-medium">Peak risk elevated to HIGH. Alarm triggered.</td>
                   <td className="p-4"><span className="px-2 py-1 bg-red-100 text-red-700 rounded text-base font-bold font-bold">CRITICAL</span></td>
                   <td className="p-4"><span className="text-red-600 font-bold">ACTIVE</span></td>
                </tr>
                <tr className="hover:bg-slate-50">
                   <td className="p-4 text-slate-800">16:21:21</td>
                   <td className="p-4 font-bold text-slate-700">AI FORECAST</td>
                   <td className="p-4 text-orange-600">Predicted peak of 91.4 kW exceeds 90.0 kW limit.</td>
                   <td className="p-4"><span className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-base font-bold font-bold">WARNING</span></td>
                   <td className="p-4"><span className="text-orange-600 font-bold">DETECTED</span></td>
                </tr>
                <tr className="hover:bg-slate-50">
                   <td className="p-4 text-slate-800">16:21:15</td>
                   <td className="p-4 font-bold text-slate-700">TELEMETRY</td>
                   <td className="p-4">Process Pump PMP-001 started. Load +12.5 kW.</td>
                   <td className="p-4"><span className="px-2 py-1 bg-slate-50 text-slate-800 rounded text-base font-bold font-bold">INFO</span></td>
                   <td className="p-4"><span className="text-green-600 font-bold">RECORDED</span></td>
                </tr>
                <tr className="hover:bg-slate-50">
                   <td className="p-4 text-slate-800">16:21:03</td>
                   <td className="p-4 font-bold text-slate-700">TELEMETRY</td>
                   <td className="p-4">Air Compressor CMP-001 started. Load +21.4 kW.</td>
                   <td className="p-4"><span className="px-2 py-1 bg-slate-50 text-slate-800 rounded text-base font-bold font-bold">INFO</span></td>
                   <td className="p-4"><span className="text-green-600 font-bold">RECORDED</span></td>
                </tr>
             </tbody>
          </table>
       </div>
    </div>
  )
}
