"use client"
import React, { useState, useEffect } from 'react'

export function LiveMeterPlaceholder({ title }: { title?: string }) {
  const [telemetry, setTelemetry] = useState<any>(null)
  
  useEffect(() => {
    let isMounted = true
    const fetchTelemetry = async () => {
       try {
          const res = await fetch('/api/telemetry/latest')
          if (res.ok && isMounted) setTelemetry(await res.json())
       } catch (e) {}
    }
    
    fetchTelemetry()
    const tid = setInterval(fetchTelemetry, 1000)
    
    return () => { isMounted = false; clearInterval(tid) }
  }, [])

  const isConnected = telemetry?.status === 'CONNECTED'
  const isOffline = telemetry?.status === 'OFFLINE' || telemetry?.status === 'NO_DATA'
  const reading = telemetry?.reading

  return (
    <div className="flex-1 flex items-center justify-center bg-white p-4 min-h-[60vh] rounded-xl m-6">
      <div className="max-w-2xl w-full">
         <div className="flex items-center justify-between mb-8 border-b border-slate-300 pb-4">
            <div>
               <div className="text-base font-bold text-slate-500 uppercase tracking-widest mb-1">Live Telemetry View</div>
               <div className="text-4xl lg:text-5xl font-bold text-slate-800 uppercase tracking-tight">{title || 'Live Meter'}</div>
            </div>
            {isConnected ? (
               <div className="flex items-center gap-2 text-teal-700 font-bold text-base font-bold uppercase tracking-widest border-2 border-teal-200 bg-teal-50 px-3 py-1 rounded">
                  <div className="w-2 h-2 rounded-full bg-teal-500 animate-pulse"></div>
                  CONNECTED
               </div>
            ) : (
               <div className="flex items-center gap-2 text-red-500 font-bold text-base font-bold uppercase tracking-widest border-2 border-red-200 bg-red-50 px-3 py-1 rounded">
                  <div className="w-2 h-2 rounded-full bg-red-500"></div>
                  OFFLINE
               </div>
            )}
         </div>

         {isConnected && reading ? (
            <div className="space-y-6">
               <div className="grid grid-cols-2 gap-4 text-base font-bold font-mono">
                  <div className="bg-slate-50 p-5 rounded border border-slate-200">
                     <span className="text-slate-500 block mb-1 uppercase text-xs font-bold tracking-widest">Source</span>
                     <span className="text-teal-700 font-bold">{reading.data_source} &rarr; L&T Meter</span>
                  </div>
                  <div className="bg-slate-50 p-5 rounded border border-slate-200">
                     <span className="text-slate-500 block mb-1 uppercase text-xs font-bold tracking-widest">Device</span>
                     <span className="text-slate-800 font-bold">{reading.asset_id}</span>
                  </div>
                  <div className="bg-slate-50 p-5 rounded border border-slate-200">
                     <span className="text-slate-500 block mb-1 uppercase text-xs font-bold tracking-widest">Last Update</span>
                     <span className="text-slate-800">{new Date(reading.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div className="bg-slate-50 p-5 rounded border border-slate-200">
                     <span className="text-slate-500 block mb-1 uppercase text-xs font-bold tracking-widest">Data Age</span>
                     <span className="text-teal-700 font-bold">{telemetry.data_age_seconds} sec</span>
                  </div>
               </div>

               <div className="grid grid-cols-2 md:grid-cols-3 gap-4 font-mono">
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                     <div className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-1">Watts Total (40101)</div>
                     <div className="text-2xl font-bold text-teal-700">{(reading.watts_total ?? (Number(reading.active_power_kw || 0) * 1000)).toFixed(1)} <span className="text-sm font-bold text-slate-500">W</span></div>
                     <div className="text-[11px] text-slate-400">{(Number(reading.active_power_kw || 0)).toFixed(3)} kW</div>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                     <div className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-1">VA Total (40125)</div>
                     <div className="text-2xl font-bold text-slate-800">{(reading.va_total ?? (Number(reading.watts_total || 0) / (reading.pf_avg || 0.95))).toFixed(1)} <span className="text-sm font-bold text-slate-500">VA</span></div>
                     <div className="text-[11px] text-slate-400">3-Phase Apparent</div>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                     <div className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-1">V_LN Avg (40141)</div>
                     <div className="text-2xl font-bold text-slate-800">{(reading.v_ln_avg ?? (reading.voltage_v || 230)).toFixed(1)} <span className="text-sm font-bold text-slate-500">V</span></div>
                     <div className="text-[11px] text-slate-400">LL: {(reading.v_ll_avg ?? ((reading.voltage_v || 230) * 1.732)).toFixed(1)} V</div>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                     <div className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-1">Current Total (40149)</div>
                     <div className="text-2xl font-bold text-slate-800">{(reading.current_total ?? (reading.current_a || 0)).toFixed(2)} <span className="text-sm font-bold text-slate-500">A</span></div>
                     <div className="text-[11px] text-slate-400">3-Phase Sum</div>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                     <div className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-1">Frequency (40157)</div>
                     <div className="text-2xl font-bold text-slate-800">{(reading.frequency ?? (reading.frequency_hz || 50)).toFixed(2)} <span className="text-sm font-bold text-slate-500">Hz</span></div>
                     <div className="text-[11px] text-slate-400">PF: {(reading.pf_avg ?? (reading.power_factor || 0.95)).toFixed(3)}</div>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                     <div className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-1">Load Hours (40217)</div>
                     <div className="text-2xl font-bold text-slate-800">{reading.load_hours ?? 1420} <span className="text-sm font-bold text-slate-500">hrs</span></div>
                     <div className="text-[11px] text-slate-400">Wh: {(reading.energy_wh ?? (Number(reading.energy_kwh || 0) * 1000)).toFixed(0)}</div>
                  </div>
               </div>
            </div>
         ) : (
            <div className="text-center py-10">
               {reading && (
                  <div className="text-base font-bold text-slate-800 font-mono mb-6 space-y-2">
                     <div>Last telemetry: {new Date(reading.timestamp).toLocaleTimeString()}</div>
                     <div className="text-red-400">Data age: {telemetry.data_age_seconds} seconds</div>
                  </div>
               )}
               <div className="inline-flex flex-col items-center justify-center p-5 border border-slate-200 border-dashed rounded-xl bg-slate-50">
                  <div className="w-12 h-12 mb-4 text-slate-400">
                     <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                  </div>
                  <h3 className="text-lg font-bold text-slate-700 uppercase tracking-widest mb-2">Waiting for Telemetry</h3>
                  <p className="text-sm font-semibold text-slate-500 max-w-[250px] leading-relaxed">
                     Hardware disconnected. Connect the Raspberry Pi L&T Meter to resume live mode.
                  </p>
               </div>
            </div>
         )}
      </div>
    </div>
  )
}
