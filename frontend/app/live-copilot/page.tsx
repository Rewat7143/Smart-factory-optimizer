"use client"
import React, { useEffect, useState } from 'react'

export default function LiveCopilotPage() {
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
  const cp = isOffline ? [] : data.copilot;

  return (
    <div className="p-4 font-mono space-y-6 h-full flex flex-col">
      <header className="mb-4">
        <h1 className="text-xl lg:text-xl lg:text-2xl font-bold font-bold text-slate-800 uppercase tracking-tight">Live Industrial Copilot</h1>
        <p className="text-base font-bold font-bold tracking-widest text-slate-800 uppercase mt-1">Real-Time Electrical Guidance</p>
      </header>
      
      {isOffline && (
        <div className="bg-red-50 border-2 border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center font-bold text-lg font-bold">
          <span className="w-2 h-2 rounded-full bg-red-600 text-white animate-pulse mr-3"></span>
          OFFLINE: Hardware disconnected. Waiting for meter telemetry.
        </div>
      )}

      <div className="flex-1 bg-white border-2 border-slate-200 rounded-xl shadow-sm p-4 overflow-y-auto">
         {cp.length === 0 ? (
            <div className="flex items-center justify-center h-full text-slate-800 font-bold text-lg font-bold">
               {isOffline ? 'Hardware disconnected. Copilot offline.' : 'No urgent insights. Grid and power factors nominal.'}
            </div>
         ) : (
            <div className="space-y-4">
               {cp.map((insight: any, i: number) => (
                  <div key={i} className={`p-4 rounded-lg border-2 flex gap-4 ${insight.type === 'ACTION' ? 'bg-teal-50 border-teal-200 text-teal-900' : insight.type === 'WARNING' ? 'bg-amber-50 border-amber-200 text-amber-900' : 'bg-slate-50 border-slate-200 text-slate-700'}`}>
                     <div className="text-xl lg:text-2xl font-bold mt-1">
                        {insight.type === 'ACTION' ? '🤖' : insight.type === 'WARNING' ? '⚠️' : '💡'}
                     </div>
                     <div>
                        <div className="text-base font-bold uppercase font-bold tracking-widest opacity-60 mb-1">{insight.type}</div>
                        <div className="font-bold text-lg font-bold">{insight.message}</div>
                     </div>
                  </div>
               ))}
            </div>
         )}
      </div>
    </div>
  );
}
