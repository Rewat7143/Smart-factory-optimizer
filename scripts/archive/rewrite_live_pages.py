import os

live_command = """"use client"
import React, { useEffect, useState } from 'react'
import ReactECharts from 'echarts-for-react'

export default function LiveCommandPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<boolean>(true);
  const [history, setHistory] = useState<{time: string, power: number}[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
        const res = await fetch(`${apiUrl}/live/dashboard`);
        if (!res.ok) { setError(true); return; }
        const json = await res.json();
        if (json.status === 'OFFLINE') { setError(true); return; }
        
        setData(json);
        setError(false);
        const now = new Date().toLocaleTimeString();
        setHistory(prev => {
          const newArr = [...prev, { time: now, power: json.metrics.power_kw }];
          if (newArr.length > 30) newArr.shift();
          return newArr;
        });
      } catch (err) { setError(true); }
    };
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const isOffline = error || !data;
  const m = isOffline ? { power_kw: '####', voltage: '####', current: '####', pf: '####', freq: '####' } : data.metrics;
  const q = isOffline ? { alerts: ['Hardware Disconnected - No Telemetry Available'] } : data.quality;

  const chartOptions = {
    animation: false,
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: history.map(d => d.time), axisLabel: { color: '#94a3b8', fontSize: 10 } },
    yAxis: { type: 'value', name: 'Power (kW)', nameTextStyle: { color: '#94a3b8', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { color: '#f1f5f9' } } },
    series: [{ data: history.map(d => d.power), type: 'line', smooth: true, lineStyle: { color: '#3b82f6', width: 3 }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(59, 130, 246, 0.2)' }, { offset: 1, color: 'rgba(59, 130, 246, 0)' }] } }, itemStyle: { color: '#3b82f6' } }],
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true }
  };

  return (
    <div className="p-6 font-mono space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-black text-slate-900 uppercase tracking-tighter">Live Command Center</h1>
        <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mt-1">L&T WL4400 Real-Time Telemetry</p>
      </header>

      {isOffline && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center font-bold text-sm">
          <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse mr-3"></span>
          OFFLINE: Hardware disconnected. Waiting for meter telemetry.
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <div className="text-[10px] uppercase tracking-widest font-bold text-slate-400">Active Power</div>
          <div className="text-2xl font-black text-slate-900 mt-2">{m.power_kw} {m.power_kw !== '####' && <span className="text-sm font-bold text-slate-400">kW</span>}</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <div className="text-[10px] uppercase tracking-widest font-bold text-slate-400">Voltage</div>
          <div className="text-2xl font-black text-slate-900 mt-2">{m.voltage} {m.voltage !== '####' && <span className="text-sm font-bold text-slate-400">V</span>}</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <div className="text-[10px] uppercase tracking-widest font-bold text-slate-400">Current</div>
          <div className="text-2xl font-black text-slate-900 mt-2">{m.current} {m.current !== '####' && <span className="text-sm font-bold text-slate-400">A</span>}</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <div className="text-[10px] uppercase tracking-widest font-bold text-slate-400">Power Factor</div>
          <div className={`text-2xl font-black mt-2 ${(m.pf !== '####' && m.pf < 0.95) ? 'text-amber-600' : 'text-slate-900'}`}>{m.pf}</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <div className="text-[10px] uppercase tracking-widest font-bold text-slate-400">Frequency</div>
          <div className="text-2xl font-black text-slate-900 mt-2">{m.freq} {m.freq !== '####' && <span className="text-sm font-bold text-slate-400">Hz</span>}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <div className="text-[10px] uppercase tracking-widest font-bold text-slate-400 mb-4">Real-Time Active Power (kW)</div>
          <ReactECharts option={chartOptions} style={{ height: '300px' }} />
        </div>
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 flex flex-col">
          <div className="text-[10px] uppercase tracking-widest font-bold text-slate-400 mb-4">Active Alerts</div>
          <div className="flex-1 space-y-3 overflow-y-auto">
            {q.alerts.length === 0 ? (
              <div className="text-sm font-bold text-slate-400">No active alerts. System nominal.</div>
            ) : (
              q.alerts.map((alert: string, i: number) => (
                <div key={i} className={`p-3 border rounded-lg text-sm font-bold ${isOffline ? 'bg-slate-50 border-slate-200 text-slate-600' : 'bg-amber-50 border-amber-200 text-amber-900'}`}>
                  {isOffline ? '---' : '⚠️'} {alert}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
"""

live_quality = """"use client"
import React, { useEffect, useState } from 'react'

export default function LiveQualityPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
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
  const m = isOffline ? { pf: '####', freq: '####' } : data.metrics;
  
  const isPfBad = !isOffline && m.pf < 0.95;
  const freqDev = !isOffline ? Math.abs(50.0 - m.freq).toFixed(2) : '####';
  const isFreqBad = !isOffline && parseFloat(freqDev as string) > 0.5;

  return (
    <div className="p-6 font-mono space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-black text-slate-900 uppercase tracking-tighter">Power Quality & Maintenance</h1>
        <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mt-1">Live Diagnostics</p>
      </header>
      
      {isOffline && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center font-bold text-sm">
          <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse mr-3"></span>
          OFFLINE: Hardware disconnected. Waiting for meter telemetry.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className={`bg-white border-2 rounded-xl shadow-sm p-6 ${isPfBad ? 'border-amber-400' : 'border-slate-200'}`}>
          <div className="text-[10px] uppercase tracking-widest font-bold text-slate-400">Power Factor (PF)</div>
          <div className={`text-5xl font-black mt-4 ${isPfBad ? 'text-amber-600' : 'text-slate-900'}`}>{isOffline ? '####' : m.pf.toFixed(2)}</div>
          <div className="mt-6 p-4 rounded-lg bg-slate-50 border border-slate-100">
            <div className="text-[10px] uppercase font-bold text-slate-500 mb-1">Status</div>
            {isOffline ? (
              <div className="text-sm font-bold text-slate-400">Waiting for data...</div>
            ) : isPfBad ? (
              <div className="text-sm font-bold text-amber-600">WARNING: PF below 0.95. High risk of reactive power penalties. Capacitor bank intervention recommended.</div>
            ) : (
              <div className="text-sm font-bold text-emerald-600">NOMINAL: PF within healthy range. No penalties expected.</div>
            )}
          </div>
        </div>

        <div className={`bg-white border-2 rounded-xl shadow-sm p-6 ${isFreqBad ? 'border-red-400' : 'border-slate-200'}`}>
          <div className="text-[10px] uppercase tracking-widest font-bold text-slate-400">Grid Frequency</div>
          <div className="flex items-baseline space-x-2 mt-4">
            <div className={`text-5xl font-black ${isFreqBad ? 'text-red-600' : 'text-slate-900'}`}>{isOffline ? '####' : m.freq.toFixed(2)}</div>
            <div className="text-xl font-bold text-slate-400">Hz</div>
          </div>
          <div className="mt-6 p-4 rounded-lg bg-slate-50 border border-slate-100">
            <div className="text-[10px] uppercase font-bold text-slate-500 mb-1">Stability Analysis</div>
            <div className="text-sm font-bold text-slate-700">Deviation from 50Hz: <span className={isFreqBad ? 'text-red-600' : 'text-slate-900'}>{freqDev} Hz</span></div>
            {isFreqBad && <div className="text-xs font-bold text-red-500 mt-2">CRITICAL: Frequency deviation exceeds safe limits. Equipment damage risk.</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
"""

live_economics = """"use client"
import React, { useEffect, useState } from 'react'

export default function LiveEconomicsPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
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
    <div className="p-6 font-mono space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-black text-slate-900 uppercase tracking-tighter">Live Economics</h1>
        <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mt-1">Real-Time Cost Tracking</p>
      </header>

      {isOffline && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center font-bold text-sm">
          <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse mr-3"></span>
          OFFLINE: Hardware disconnected. Waiting for meter telemetry.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <div className="text-[10px] uppercase tracking-widest font-bold text-slate-400">Real-Time Accumulated Energy</div>
          <div className="text-4xl font-black text-slate-900 mt-4">{isOffline ? '####' : m.energy_kwh.toFixed(2)} <span className="text-lg font-bold text-slate-400">kWh</span></div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <div className="text-[10px] uppercase tracking-widest font-bold text-slate-400">Current Session Cost</div>
          <div className="text-4xl font-black text-slate-900 mt-4">₹{isOffline ? '####' : m.cost_inr.toFixed(2)}</div>
        </div>
      </div>
      
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <div className="text-[10px] uppercase tracking-widest font-bold text-slate-400 mb-4">Projected Monthly Liability</div>
          <div className="text-6xl font-black text-green-700">
             ₹{isOffline ? '####' : (m.cost_inr * 30).toLocaleString('en-IN', {maximumFractionDigits: 0})}
          </div>
          <div className="mt-4 text-xs font-bold text-slate-500">Based on flat tariff of ₹7.5 / kWh assuming continuous operation.</div>
      </div>
    </div>
  );
}
"""

live_twin = """"use client"
import React, { useEffect, useState } from 'react'

export default function LiveTwinPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
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
    <div className="p-6 font-mono space-y-6 h-full flex flex-col">
      <header className="mb-4">
        <h1 className="text-3xl font-black text-slate-900 uppercase tracking-tighter">Electrical Twin</h1>
        <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mt-1">Single-Line Power Flow</p>
      </header>
      
      {isOffline && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-2 flex items-center font-bold text-sm">
          <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse mr-3"></span>
          OFFLINE: Hardware disconnected. Waiting for meter telemetry.
        </div>
      )}

      <div className="flex-1 bg-white border border-slate-200 rounded-xl shadow-sm p-10 flex flex-col items-center justify-center space-y-8 relative overflow-hidden">
        
        {/* Animated Background Flow */}
        {!isOffline && (
            <div className="absolute inset-0 pointer-events-none opacity-5">
               <div className="w-full h-full bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] animate-[pulse_4s_ease-in-out_infinite]"></div>
            </div>
        )}

        {/* Node 1: Grid */}
        <div className="w-64 border-2 border-blue-400 bg-blue-50 rounded-lg p-4 text-center shadow-lg relative z-10">
           <div className="text-[10px] font-bold tracking-widest uppercase text-blue-500 mb-2">Source</div>
           <div className="font-black text-blue-900 text-xl">Utility Grid</div>
           <div className="mt-3 flex justify-between text-xs font-bold text-blue-800">
              <span>{isOffline ? '####' : data.twin.nodes[0].voltage.toFixed(1)} V</span>
              <span>{isOffline ? '####' : data.twin.nodes[0].freq.toFixed(2)} Hz</span>
           </div>
        </div>

        {/* Arrow Down */}
        <div className="h-16 border-l-4 border-dashed border-slate-300 relative z-10">
           {!isOffline && <div className="absolute -left-[6px] top-0 w-2 h-2 rounded-full bg-blue-500 animate-[ping_1s_infinite]"></div>}
        </div>

        {/* Node 2: Meter */}
        <div className="w-80 border-2 border-slate-700 bg-slate-900 rounded-lg p-6 text-center shadow-2xl relative z-10 transform transition-transform hover:scale-105">
           <div className="text-[10px] font-bold tracking-widest uppercase text-slate-400 mb-2">Main Incomer</div>
           <div className="font-black text-white text-2xl mb-1">L&T WL4400</div>
           <div className="text-[10px] text-emerald-400 mb-4">{isOffline ? 'OFFLINE' : 'LIVE MODBUS RTU'}</div>
           <div className="grid grid-cols-3 gap-2 text-xs font-bold text-slate-300 bg-slate-800 p-3 rounded">
              <div><div className="text-[9px] text-slate-500 mb-1">POWER</div>{isOffline ? '####' : data.twin.nodes[1].power_kw.toFixed(1)}kW</div>
              <div className="border-l border-r border-slate-700"><div className="text-[9px] text-slate-500 mb-1">CURRENT</div>{isOffline ? '####' : data.twin.nodes[1].current_a.toFixed(1)}A</div>
              <div><div className="text-[9px] text-slate-500 mb-1">PF</div>{isOffline ? '####' : data.twin.nodes[1].pf.toFixed(2)}</div>
           </div>
        </div>

        {/* Arrow Down */}
        <div className="h-16 border-l-4 border-dashed border-slate-300 relative z-10">
           {!isOffline && <div className="absolute -left-[6px] top-4 w-2 h-2 rounded-full bg-blue-500 animate-[ping_1s_infinite_200ms]"></div>}
        </div>

        {/* Node 3: Factory Load */}
        <div className="w-96 border-2 border-slate-200 bg-white rounded-lg p-6 text-center shadow-lg relative z-10">
           <div className="text-[10px] font-bold tracking-widest uppercase text-slate-400 mb-2">Distribution</div>
           <div className="font-black text-slate-800 text-xl mb-4">Aggregated Factory Load</div>
           
           <div className="w-full bg-slate-100 rounded-full h-4 overflow-hidden relative">
              {!isOffline && <div className="bg-blue-500 h-full" style={{ width: `${Math.min(100, (data.twin.nodes[2].power_kw / 100)*100)}%` }}></div>}
           </div>
           <div className="mt-2 text-xs font-bold text-slate-500 flex justify-between">
              <span>0 kW</span>
              <span className="text-blue-600">{isOffline ? '####' : data.twin.nodes[2].power_kw.toFixed(1)} kW</span>
              <span>100 kW</span>
           </div>
        </div>

      </div>
    </div>
  );
}
"""

live_copilot = """"use client"
import React, { useEffect, useState } from 'react'

export default function LiveCopilotPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
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
    <div className="p-6 font-mono space-y-6 h-full flex flex-col">
      <header className="mb-4">
        <h1 className="text-3xl font-black text-slate-900 uppercase tracking-tighter">Live AI Copilot</h1>
        <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mt-1">Real-Time Electrical Guidance</p>
      </header>
      
      {isOffline && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center font-bold text-sm">
          <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse mr-3"></span>
          OFFLINE: Hardware disconnected. Waiting for meter telemetry.
        </div>
      )}

      <div className="flex-1 bg-white border border-slate-200 rounded-xl shadow-sm p-6 overflow-y-auto">
         {cp.length === 0 ? (
            <div className="flex items-center justify-center h-full text-slate-400 font-bold text-sm">
               {isOffline ? 'Hardware disconnected. AI offline.' : 'No urgent insights. Grid and power factors nominal.'}
            </div>
         ) : (
            <div className="space-y-4">
               {cp.map((insight: any, i: number) => (
                  <div key={i} className={`p-4 rounded-lg border flex gap-4 ${insight.type === 'ACTION' ? 'bg-blue-50 border-blue-200 text-blue-900' : insight.type === 'WARNING' ? 'bg-amber-50 border-amber-200 text-amber-900' : 'bg-slate-50 border-slate-200 text-slate-700'}`}>
                     <div className="text-2xl mt-1">
                        {insight.type === 'ACTION' ? '🤖' : insight.type === 'WARNING' ? '⚠️' : '💡'}
                     </div>
                     <div>
                        <div className="text-[10px] uppercase font-bold tracking-widest opacity-60 mb-1">{insight.type}</div>
                        <div className="font-bold text-sm">{insight.message}</div>
                     </div>
                  </div>
               ))}
            </div>
         )}
      </div>
    </div>
  );
}
"""

with open('frontend/app/live-command/page.tsx', 'w') as f: f.write(live_command)
with open('frontend/app/live-quality/page.tsx', 'w') as f: f.write(live_quality)
with open('frontend/app/live-economics/page.tsx', 'w') as f: f.write(live_economics)
with open('frontend/app/live-twin/page.tsx', 'w') as f: f.write(live_twin)
with open('frontend/app/live-copilot/page.tsx', 'w') as f: f.write(live_copilot)

