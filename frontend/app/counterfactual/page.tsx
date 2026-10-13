"use client"
import React, { useState, useEffect } from 'react'

export default function Counterfactual() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let isMounted = true
    const fetchCompare = async () => {
      try {
        const res = await fetch(`${(typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))}/counterfactual/compare`)
        if (res.ok && isMounted) {
          setData(await res.json())
          setLoading(false)
        }
      } catch (e) {}
    }
    fetchCompare()
    const interval = setInterval(fetchCompare, 3000)
    return () => { isMounted = false; clearInterval(interval) }
  }, [])

  return (
    
      <div className="max-w-[1600px] mx-auto space-y-6 font-mono text-slate-800 pb-20">
        <div className="flex justify-between items-end border-b border-slate-200 pb-4">
          <div>
            <h1 className="text-xl lg:text-2xl font-bold font-bold tracking-tight text-slate-800 uppercase">Scenario Engine</h1>
            <p className="text-base font-bold text-slate-800 uppercase tracking-widest font-bold mt-1">Counterfactual Comparison</p>
          </div>
        </div>

        {loading ? (
           <div className="p-10 font-mono text-slate-800">GENERATING COUNTERFACTUALS...</div>
        ) : (
           <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                 {data?.scenarios?.map((scen: any) => {
                   let borderColor = 'border-slate-200';
                   let banner = null;
                   
                   if (scen.type === 'CURRENT') {
                     borderColor = 'border-amber-400';
                   } else if (scen.type === 'AI') {
                     borderColor = 'border-green-400 shadow-[0_0_15px_rgba(74,222,128,0.3)]';
                   } else if (scen.type === 'BAD') {
                     borderColor = 'border-red-400 opacity-100';
                     banner = <div className="absolute top-4 -right-10 bg-red-600 text-white text-slate-800 text-lg font-bold font-bold uppercase font-bold tracking-widest py-1 px-10 rotate-45">REJECTED</div>;
                   }

                   return (
                     <div key={scen.type} className={`bg-white border-2 rounded-xl p-4 relative overflow-hidden ${borderColor}`}>
                       {banner}
                       {scen.type === 'BAD' && <div className="bg-red-100 text-red-700 text-base font-bold uppercase font-bold tracking-widest p-2 mb-4 text-center rounded">Production Constraint Violated</div>}
                       
                       <div className="text-lg font-bold font-bold text-slate-800 mb-1">{scen.name}</div>
                       <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800 mb-6">{scen.description}</div>

                       <div className="space-y-4">
                          <div>
                            <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800 mb-1">Peak Load</div>
                            <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">{scen.peak_kw} <span className="text-base font-bold">kW</span></div>
                          </div>
                          
                          <div>
                            <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800 mb-1">Cost</div>
                            <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">₹{scen.cost_inr}</div>
                          </div>

                          <div>
                            <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800 mb-1">Production Kept</div>
                            <div className={`text-xl lg:text-2xl font-bold font-bold ${scen.production_percent < 100 ? 'text-red-500 line-through' : 'text-slate-800'}`}>{scen.production_percent}%</div>
                          </div>
                       </div>

                       <div className="mt-6 pt-4 border-t border-slate-100">
                          <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800 mb-2">Actions Taken</div>
                          <ul className="text-base font-bold text-slate-800 space-y-1">
                            {scen.actions_taken?.map((act: string, i: number) => (
                              <li key={i}>- {act}</li>
                            ))}
                            {!scen.actions_taken?.length && <li>- None</li>}
                          </ul>
                       </div>
                     </div>
                   )
                 })}
              </div>

              <div className="bg-white text-slate-800 rounded-xl shadow-sm p-4 text-center">
                 <div className="text-lg font-bold font-bold tracking-widest uppercase text-green-400">
                    AI saves ₹{data?.savings_inr || 0}/day while maintaining 100% production
                 </div>
              </div>
           </div>
        )}
      </div>
    
  )
}
