"use client"
import React, { useState, useEffect } from 'react'
import { useGlobalState } from './GlobalState'

export function SimulationDrawer() {
  const { mode } = useGlobalState()
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [state, setState] = useState<any>(null)

  // Fetch current simulation state
  const fetchSimState = async () => {
    try {
      const res = await fetch(`${(typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))}/factory/state`)
      if (res.ok) setState(await res.json())
    } catch (e) {}
  }

  useEffect(() => {
    if (mode === 'SIMULATION' && isOpen) fetchSimState()
  }, [mode, isOpen])

  const handleUpdate = async (payload: any) => {
    setLoading(true)
    try {
      await fetch(`${(typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))}/simulation/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      await fetchSimState()
    } catch (e) {}
    setLoading(false)
  }

  const handleScenario = async (scenario: string) => {
    setLoading(true)
    try {
      await fetch(`${(typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))}/simulation/scenario`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario })
      })
      await fetchSimState()
    } catch (e) {}
    setLoading(false)
  }

  if (mode !== 'SIMULATION') return null

  return (
    <>
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-white text-slate-800 px-4 py-3 rounded-full shadow-lg font-bold text-base font-bold uppercase tracking-widest flex items-center gap-2 z-40 hover:bg-slate-50 transition-all border-2 border-slate-200"
      >
        <span className="w-2 h-2 rounded-full bg-teal-500 animate-pulse"></span>
        Simulation Control
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-white/20 backdrop-blur-sm" onClick={() => setIsOpen(false)}></div>
          
          <div className="w-[450px] bg-slate-50 h-full shadow-md relative flex flex-col font-mono text-slate-800 animate-in slide-in-from-right duration-200 border-l border-slate-200">
            <div className="p-4 bg-white text-slate-800 flex justify-between items-center border-b border-slate-100">
               <div>
                 <div className="text-lg font-bold font-bold tracking-tight uppercase">Industrial Simulation</div>
                 <div className="text-lg font-bold font-bold font-bold tracking-widest text-teal-500 mt-1 uppercase">Live Engineering Sandbox</div>
               </div>
               <button onClick={() => setIsOpen(false)} className="text-slate-800 hover:text-slate-800">✕</button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-8">
               
               {/* PRESETS */}
               <div className="space-y-3">
                 <div className="text-base font-bold font-bold text-slate-800 uppercase tracking-widest">Scenario Presets</div>
                 <div className="grid grid-cols-2 gap-2">
                    <button onClick={() => handleScenario('NORMAL')} className="bg-white border-2 border-slate-200 rounded p-2 text-lg font-bold font-bold font-bold uppercase tracking-widest hover:border-slate-400 text-left">Normal Factory</button>
                    <button onClick={() => handleScenario('PEAK_EVENT')} className="bg-white border-2 border-slate-200 rounded p-2 text-lg font-bold font-bold font-bold uppercase tracking-widest hover:border-red-400 text-red-600 text-left">Peak Event</button>
                    <button onClick={() => handleScenario('SURGE')} className="bg-white border-2 border-slate-200 rounded p-2 text-lg font-bold font-bold font-bold uppercase tracking-widest hover:border-slate-400 text-left">Production Surge</button>
                    <button onClick={() => handleScenario('COMPRESSOR_FAILURE')} className="bg-white border-2 border-slate-200 rounded p-2 text-lg font-bold font-bold font-bold uppercase tracking-widest hover:border-amber-400 text-amber-600 text-left">CMP-001 Failure</button>
                 </div>
               </div>

               <hr className="border-slate-200" />

               {/* FACTORY CONTROLS */}
               <div className="space-y-5">
                 <div className="text-base font-bold font-bold text-slate-800 uppercase tracking-widest flex justify-between">
                    <span>Global Parameters</span>
                    {loading && <span className="text-teal-600">APPLYING...</span>}
                 </div>

                 <div className="bg-white p-4 rounded border-2 border-slate-200 space-y-4 shadow-sm">
                    <div>
                       <div className="flex justify-between text-base font-bold font-bold mb-2">
                          <span>Demand Limit</span>
                          <span className="text-red-500">{state?.contract_demand_kw || 100} kW</span>
                       </div>
                       <input type="range" min="50" max="200" value={state?.contract_demand_kw || 100} 
                          onChange={(e) => handleUpdate({ contract_demand_kw: Number(e.target.value) })}
                          className="w-full accent-slate-900" />
                    </div>
                    <div>
                       <div className="flex justify-between text-base font-bold font-bold mb-2">
                          <span>Production Target</span>
                          <span className="text-emerald-600">{state?.production_target_percent || 100} %</span>
                       </div>
                       <input type="range" min="50" max="150" value={state?.production_target_percent || 100} 
                          onChange={(e) => handleUpdate({ production_target_percent: Number(e.target.value) })}
                          className="w-full accent-slate-900" />
                    </div>
                 </div>
               </div>

               <hr className="border-slate-200" />

               {/* MACHINE CONTROLS */}
               <div className="space-y-3">
                 <div className="text-base font-bold font-bold text-slate-800 uppercase tracking-widest">Machine Parameters</div>
                 <div className="space-y-3">
                    {state?.assets?.map((a: any) => (
                       <div key={a.id || a.asset_id} className="bg-white p-4 rounded border-2 border-slate-200 shadow-sm space-y-3">
                          <div className="flex justify-between items-center border-b border-slate-100 pb-2">
                             <div className="font-bold text-base font-bold">{a.name}</div>
                             <div className={`text-lg font-bold font-bold px-2 py-0.5 rounded font-bold uppercase tracking-widest ${a.status === 'RUNNING' || a.state === 'RUNNING' ? 'bg-emerald-100 text-emerald-700' : a.status === 'FAULT' || a.state === 'FAULT' ? 'bg-red-100 text-red-700' : 'bg-slate-50 text-slate-800'}`}>
                                {a.status || a.state}
                             </div>
                          </div>
                          
                          <div className="flex items-center gap-4">
                             <div className="flex-1">
                                <div className="text-lg font-bold font-bold font-bold text-slate-800 uppercase mb-1">Power Draw (kW)</div>
                                <input type="number" 
                                   value={a.power_kw || a.operating_power_kw || 0}
                                   onChange={(e) => handleUpdate({ assets: { [a.id || a.asset_id]: { operating_power_kw: Number(e.target.value) } } })}
                                   className="w-full border-2 border-slate-200 rounded p-1 text-base font-bold font-mono font-bold" />
                             </div>
                             
                             <div className="flex-1">
                                <div className="text-lg font-bold font-bold font-bold text-slate-800 uppercase mb-1">Status Action</div>
                                <select 
                                   value={a.status || a.state}
                                   onChange={(e) => handleUpdate({ assets: { [a.id || a.asset_id]: { status: e.target.value } } })}
                                   className="w-full border-2 border-slate-200 rounded p-1 text-base font-bold font-mono">
                                   <option value="RUNNING">RUNNING</option>
                                   <option value="OFF">OFF</option>
                                   <option value="FAULT">FAULT</option>
                                </select>
                             </div>
                          </div>
                       </div>
                    ))}
                 </div>
               </div>

            </div>
          </div>
        </div>
      )}
    </>
  )
}
