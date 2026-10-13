"use client"
import React, { useEffect, useState } from 'react'

export default function LiveTwinPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = (typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))
        const res = await fetch(`${apiUrl}/live/dashboard`);
        if (!res.ok) { setError(true); return; }
        const json = await res.json();
        if (json.status === 'OFFLINE') { setError(true); return; }
        setData(json);
        setError(false);
      } catch (err) { setError(true); }
    };
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const isOffline = error || !data;
  
  return (
    <div className="p-4 font-mono space-y-6 h-full flex flex-col">
      <header className="mb-4">
        <h1 className="text-xl lg:text-xl lg:text-2xl font-bold font-bold text-slate-800 uppercase tracking-tight">Electrical Twin</h1>
        <p className="text-base font-bold font-bold tracking-widest text-slate-800 uppercase mt-1">Single-Line Power Flow</p>
      </header>
      
      {isOffline && (
        <div className="bg-red-50 border-2 border-red-200 text-red-700 px-4 py-3 rounded-lg mb-2 flex items-center font-bold text-lg font-bold">
          <span className="w-2 h-2 rounded-full bg-red-600 text-white animate-pulse mr-3"></span>
          OFFLINE: Hardware disconnected. Waiting for meter telemetry.
        </div>
      )}

      <div className="flex-1 bg-white border-2 border-slate-200 rounded-xl shadow-sm p-10 flex flex-col items-center justify-center space-y-8 relative overflow-hidden">
        
        {/* Animated Background Flow */}
        {!isOffline && (
            <div className="absolute inset-0 pointer-events-none opacity-5">
               <div className="w-full h-full bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] animate-[pulse_4s_ease-in-out_infinite]"></div>
            </div>
        )}

        {/* Node 1: Grid */}
        <div className="w-64 flex-shrink-0 border-2 border-teal-400 bg-teal-50 rounded-lg p-4 text-center shadow-lg relative z-10">
           <div className="text-base font-bold font-bold tracking-widest uppercase text-teal-600 mb-2">Source</div>
           <div className="font-bold text-teal-900 text-xl lg:text-2xl font-bold">Utility Grid</div>
           <div className="mt-3 flex justify-between text-base font-bold font-bold text-blue-800">
              <span>{isOffline ? '####' : data.twin.nodes[0].voltage.toFixed(1)} V</span>
              <span>{isOffline ? '####' : data.twin.nodes[0].freq.toFixed(2)} Hz</span>
           </div>
        </div>

        {/* Arrow Down */}
        <div className="h-16 border-l-4 border-dashed border-slate-300 relative z-10">
           {!isOffline && <div className="absolute -left-[6px] top-0 w-2 h-2 rounded-full bg-teal-500 animate-[ping_1s_infinite]"></div>}
        </div>

        {/* Node 2: Meter */}
        <div className="w-64 flex-shrink-0 border-2 border-slate-200 bg-white rounded-lg p-4 text-center shadow-md relative z-10 transform transition-transform hover:scale-105">
           <div className="text-base font-bold font-bold tracking-widest uppercase text-slate-800 mb-2">Main Incomer</div>
           <div className="font-bold text-slate-800 text-xl lg:text-2xl font-bold mb-1">L&T WL4400</div>
           <div className="text-base font-bold text-emerald-400 mb-4">{isOffline ? 'OFFLINE' : 'LIVE MODBUS RTU'}</div>
           <div className="grid grid-cols-3 gap-2 text-base font-bold font-bold text-slate-700 bg-slate-50 p-5 rounded">
              <div><div className="text-lg font-bold font-bold text-slate-800 mb-1">POWER</div>{isOffline ? '####' : data.twin.nodes[1].power_kw.toFixed(1)}kW</div>
              <div className="border-l border-r border-slate-200"><div className="text-lg font-bold font-bold text-slate-800 mb-1">CURRENT</div>{isOffline ? '####' : data.twin.nodes[1].current_a.toFixed(1)}A</div>
              <div><div className="text-lg font-bold font-bold text-slate-800 mb-1">PF</div>{isOffline ? '####' : data.twin.nodes[1].pf.toFixed(2)}</div>
           </div>
        </div>

        {/* Arrow Down */}
        <div className="h-16 border-l-4 border-dashed border-slate-300 relative z-10">
           {!isOffline && <div className="absolute -left-[6px] top-4 w-2 h-2 rounded-full bg-teal-500 animate-[ping_1s_infinite_200ms]"></div>}
        </div>

        {/* Node 3: Factory Load */}
        <div className="w-96 border-2 border-slate-200 bg-white rounded-lg p-4 text-center shadow-lg relative z-10">
           <div className="text-base font-bold font-bold tracking-widest uppercase text-slate-800 mb-2">Distribution</div>
           <div className="font-bold text-slate-800 text-xl lg:text-2xl font-bold mb-4">Aggregated Factory Load</div>
           
           <div className="w-full bg-slate-50 rounded-full h-4 overflow-hidden relative">
              {!isOffline && <div className="bg-teal-500 h-full" style={{ width: `${Math.min(100, (data.twin.nodes[2].power_kw / 100)*100)}%` }}></div>}
           </div>
           <div className="mt-2 text-base font-bold font-bold text-slate-800 flex justify-between">
              <span>0 kW</span>
              <span className="text-teal-700">{isOffline ? '####' : data.twin.nodes[2].power_kw.toFixed(1)} kW</span>
              <span>100 kW</span>
           </div>
        </div>

      </div>
    </div>
  );
}
