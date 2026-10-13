"use client"
import React, { useEffect, useState } from 'react'

export default function LiveQualityPage() {
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
    const interval = setInterval(fetchData, 1500);
    return () => clearInterval(interval);
  }, []);

  const isOffline = error || !data;
  const m = isOffline ? {} : (data.metrics || {});
  const phases = isOffline ? {} : (data.phases || {});
  const unbalance = phases.unbalance || { voltage_pct: 0, current_pct: 0 };
  
  const pfAvg = Number(m.pf_avg ?? m.pf ?? 0.95);
  const pfR = Number(m.pf_r ?? pfAvg);
  const pfY = Number(m.pf_y ?? pfAvg);
  const pfB = Number(m.pf_b ?? pfAvg);

  const isPfBad = !isOffline && pfAvg < 0.95;
  const freqVal = Number(m.frequency ?? m.freq ?? 50.0);
  const freqDev = !isOffline ? Math.abs(50.0 - freqVal).toFixed(2) : '####';
  const isFreqBad = !isOffline && parseFloat(freqDev as string) > 0.5;

  const vUnbalance = Number(unbalance.voltage_pct || 0);
  const iUnbalance = Number(unbalance.current_pct || 0);

  return (
    <div className="p-4 font-mono space-y-6 max-w-[1500px] mx-auto pb-20">
      <header className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <span className="bg-teal-700 text-white text-[10px] font-bold px-2 py-0.5 rounded uppercase">IEEE 519 / NEMA Standard</span>
          <span className="bg-slate-200 text-slate-700 text-[10px] font-bold px-2 py-0.5 rounded uppercase">Modbus 27-Param Telemetry</span>
        </div>
        <h1 className="text-2xl lg:text-3xl font-extrabold text-slate-800 uppercase tracking-tight">3-Phase Power Quality & Health</h1>
        <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mt-1">Live Waveform Symmetry & Diagnostic Engine</p>
      </header>
      
      {isOffline && (
        <div className="bg-red-50 border-2 border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center font-bold text-sm">
          <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse mr-3"></span>
          OFFLINE: Hardware disconnected. Waiting for meter telemetry stream.
        </div>
      )}

      {/* 4 PRIMARY METRICS */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* PF */}
        <div className={`bg-white border-2 rounded-xl shadow-sm p-4 ${isPfBad ? 'border-amber-400' : 'border-slate-200'}`}>
          <div className="text-xs font-bold uppercase tracking-widest text-slate-500">Power Factor (40117)</div>
          <div className={`text-2xl font-black mt-2 ${isPfBad ? 'text-amber-600' : 'text-slate-800'}`}>
            {isOffline ? '---' : pfAvg.toFixed(3)}
          </div>
          <div className="mt-3 text-xs flex justify-between font-semibold border-t border-slate-100 pt-2 text-slate-600">
            <span>R: {isOffline ? '-' : pfR.toFixed(3)}</span>
            <span>Y: {isOffline ? '-' : pfY.toFixed(3)}</span>
            <span>B: {isOffline ? '-' : pfB.toFixed(3)}</span>
          </div>
        </div>

        {/* FREQUENCY */}
        <div className={`bg-white border-2 rounded-xl shadow-sm p-4 ${isFreqBad ? 'border-red-400' : 'border-slate-200'}`}>
          <div className="text-xs font-bold uppercase tracking-widest text-slate-500">Grid Frequency (40157)</div>
          <div className={`text-2xl font-black mt-2 ${isFreqBad ? 'text-red-600' : 'text-slate-800'}`}>
            {isOffline ? '---' : `${freqVal.toFixed(2)} Hz`}
          </div>
          <div className="mt-3 text-xs font-semibold border-t border-slate-100 pt-2 text-slate-600 flex justify-between">
            <span>Deviation: {freqDev} Hz</span>
            <span className={isFreqBad ? 'text-red-600 font-bold' : 'text-emerald-600 font-bold'}>
              {isFreqBad ? 'OUT OF SPEC' : 'NOMINAL'}
            </span>
          </div>
        </div>

        {/* VOLTAGE UNBALANCE */}
        <div className={`bg-white border-2 rounded-xl shadow-sm p-4 ${vUnbalance > 2.0 ? 'border-amber-400' : 'border-slate-200'}`}>
          <div className="text-xs font-bold uppercase tracking-widest text-slate-500">Voltage Unbalance (V_unb)</div>
          <div className={`text-2xl font-black mt-2 ${vUnbalance > 2.0 ? 'text-amber-600' : 'text-slate-800'}`}>
            {isOffline ? '---' : `${vUnbalance.toFixed(2)}%`}
          </div>
          <div className="mt-3 text-xs font-semibold border-t border-slate-100 pt-2 text-slate-600 flex justify-between">
            <span>Threshold: &lt; 2.0%</span>
            <span className={vUnbalance > 2.0 ? 'text-amber-600 font-bold' : 'text-emerald-600 font-bold'}>
              {vUnbalance > 2.0 ? 'ASYMMETRIC' : 'BALANCED'}
            </span>
          </div>
        </div>

        {/* CURRENT UNBALANCE */}
        <div className={`bg-white border-2 rounded-xl shadow-sm p-4 ${iUnbalance > 15.0 ? 'border-amber-400' : 'border-slate-200'}`}>
          <div className="text-xs font-bold uppercase tracking-widest text-slate-500">Current Unbalance (I_unb)</div>
          <div className={`text-2xl font-black mt-2 ${iUnbalance > 15.0 ? 'text-amber-600' : 'text-slate-800'}`}>
            {isOffline ? '---' : `${iUnbalance.toFixed(2)}%`}
          </div>
          <div className="mt-3 text-xs font-semibold border-t border-slate-100 pt-2 text-slate-600 flex justify-between">
            <span>Threshold: &lt; 15.0%</span>
            <span className={iUnbalance > 15.0 ? 'text-amber-600 font-bold' : 'text-emerald-600 font-bold'}>
              {iUnbalance > 15.0 ? 'UNBALANCED' : 'BALANCED'}
            </span>
          </div>
        </div>
      </div>

      {/* 3-PHASE LIVE MATRIX */}
      <div className="bg-white border-2 border-slate-200 rounded-xl p-6 shadow-sm">
        <h3 className="text-xs font-bold uppercase tracking-widest text-slate-600 mb-4">
          3-Phase Phase Parameters (VR/VY/VB & IR/IY/IB & WR/WY/WB)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-rose-50/50 border border-rose-200 space-y-2">
            <div className="text-xs font-bold text-rose-700 uppercase">Phase R (Red)</div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">Voltage VR:</span> <span className="font-bold text-slate-800">{Number(m.v_r || 230).toFixed(1)} V</span></div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">Current IR:</span> <span className="font-bold text-slate-800">{Number(m.current_r || 0).toFixed(2)} A</span></div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">Power WR:</span> <span className="font-bold text-teal-700">{Number(m.watts_r || 0).toFixed(1)} W</span></div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">VA R:</span> <span className="font-bold text-slate-800">{Number(m.va_r || 0).toFixed(1)} VA</span></div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">PF R:</span> <span className="font-bold text-slate-800">{pfR.toFixed(3)}</span></div>
          </div>

          <div className="p-4 rounded-lg bg-amber-50/50 border border-amber-200 space-y-2">
            <div className="text-xs font-bold text-amber-700 uppercase">Phase Y (Yellow)</div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">Voltage VY:</span> <span className="font-bold text-slate-800">{Number(m.v_y || 230).toFixed(1)} V</span></div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">Current IY:</span> <span className="font-bold text-slate-800">{Number(m.current_y || 0).toFixed(2)} A</span></div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">Power WY:</span> <span className="font-bold text-teal-700">{Number(m.watts_y || 0).toFixed(1)} W</span></div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">VA Y:</span> <span className="font-bold text-slate-800">{Number(m.va_y || 0).toFixed(1)} VA</span></div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">PF Y:</span> <span className="font-bold text-slate-800">{pfY.toFixed(3)}</span></div>
          </div>

          <div className="p-4 rounded-lg bg-blue-50/50 border border-blue-200 space-y-2">
            <div className="text-xs font-bold text-blue-700 uppercase">Phase B (Blue)</div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">Voltage VB:</span> <span className="font-bold text-slate-800">{Number(m.v_b || 230).toFixed(1)} V</span></div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">Current IB:</span> <span className="font-bold text-slate-800">{Number(m.current_b || 0).toFixed(2)} A</span></div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">Power WB:</span> <span className="font-bold text-teal-700">{Number(m.watts_b || 0).toFixed(1)} W</span></div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">VA B:</span> <span className="font-bold text-slate-800">{Number(m.va_b || 0).toFixed(1)} VA</span></div>
            <div className="text-sm flex justify-between"><span className="text-slate-500">PF B:</span> <span className="font-bold text-slate-800">{pfB.toFixed(3)}</span></div>
          </div>
        </div>
      </div>

    </div>
  );
}
