"use client"
import React, { useEffect, useState } from 'react'

export default function LiveEconomicsPage() {
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
  const m = isOffline ? { energy_kwh: '####', cost_inr: '####' } : data.metrics;

  return (
    <div className="p-4 font-mono space-y-6">
      <header className="mb-8">
        <h1 className="text-xl lg:text-xl lg:text-2xl font-bold font-bold text-slate-800 uppercase tracking-tight">Live Economics</h1>
        <p className="text-base font-bold font-bold tracking-widest text-slate-800 uppercase mt-1">Real-Time Cost Tracking</p>
      </header>

      {isOffline && (
        <div className="bg-red-50 border-2 border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center font-bold text-lg font-bold">
          <span className="w-2 h-2 rounded-full bg-red-600 text-white animate-pulse mr-3"></span>
          OFFLINE: Hardware disconnected. Waiting for meter telemetry.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white border-2 border-slate-200 rounded-xl shadow-sm p-4">
          <div className="text-base font-bold uppercase tracking-widest font-bold text-slate-800">Real-Time Accumulated Energy</div>
          <div className="text-xl lg:text-2xl font-bold text-slate-800 mt-4">{isOffline ? '####' : m.energy_kwh.toFixed(2)} <span className="text-lg font-bold text-slate-800">kWh</span></div>
        </div>
        <div className="bg-white border-2 border-slate-200 rounded-xl shadow-sm p-4">
          <div className="text-base font-bold uppercase tracking-widest font-bold text-slate-800">Current Session Cost</div>
          <div className="text-xl lg:text-2xl font-bold text-slate-800 mt-4">₹{isOffline ? '####' : m.cost_inr.toFixed(2)}</div>
        </div>
      </div>
      
      <div className="bg-white border-2 border-slate-200 rounded-xl shadow-sm p-4">
          <div className="text-base font-bold uppercase tracking-widest font-bold text-slate-800 mb-4">Projected Monthly Liability</div>
          <div className="text-xl lg:text-xl lg:text-2xl font-bold text-green-700">
             ₹{isOffline ? '####' : (m.cost_inr * 30).toLocaleString('en-IN', {maximumFractionDigits: 0})}
          </div>
          <div className="mt-4 text-base font-bold font-bold text-slate-800">Based on flat tariff of ₹7.5 / kWh assuming continuous operation.</div>
      </div>
    </div>
  );
}
