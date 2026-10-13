"use client"
import React, { useEffect, useState } from 'react'
import ReactECharts from 'echarts-for-react'

export default function TelemetryLogPage() {
  const [data, setData] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'log' | 'memory_map'>('log');

  useEffect(() => {
    const fetchTelemetry = async () => {
      const baseUrl = (typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : 'http://localhost:8000/api')
      const res = await fetch(`${baseUrl}/telemetry/history`)
      if (res.ok) setData(await res.json())
    }
    fetchTelemetry();
    const int = setInterval(fetchTelemetry, 1500);
    return () => clearInterval(int);
  }, []);

  if (!data) return <div className="p-8 text-slate-800 font-bold font-mono">Loading Telemetry Ledger...</div>

  const history = data.history || [];
  
  if (history.length === 0) {
      return (
         <div className="max-w-[1600px] mx-auto space-y-8 font-mono text-slate-800 p-6">
            <h1 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-800 uppercase">Hardware Telemetry</h1>
            <div className="bg-slate-100 border border-slate-300 p-12 text-center rounded-xl">
               <div className="text-xl font-bold text-slate-500 uppercase tracking-widest">Waiting For Telemetry</div>
               <div className="text-sm font-semibold text-slate-400 mt-2">No historical meter readings stored in the current session. Start the simulator in terminal to stream live telemetry.</div>
            </div>
         </div>
      )
  }

  const latest = history[history.length - 1];
  const timestamps = history.slice(-40).map((r: any) => new Date(r.timestamp).toISOString().substring(11, 19));
  const powerData = history.slice(-40).map((r: any) => Number(r.active_power_kw ?? (r.watts_total ? r.watts_total / 1000 : 0)));
  const currR = history.slice(-40).map((r: any) => Number(r.current_r ?? (r.current_a ? r.current_a / 3 : 0)));
  const currY = history.slice(-40).map((r: any) => Number(r.current_y ?? (r.current_a ? r.current_a / 3 : 0)));
  const currB = history.slice(-40).map((r: any) => Number(r.current_b ?? (r.current_a ? r.current_a / 3 : 0)));

  const voltR = history.slice(-40).map((r: any) => Number(r.v_r ?? (r.voltage_v ?? 230)));
  const voltY = history.slice(-40).map((r: any) => Number(r.v_y ?? (r.voltage_v ?? 230)));
  const voltB = history.slice(-40).map((r: any) => Number(r.v_b ?? (r.voltage_v ?? 230)));

  const currentChart = {
    animation: false,
    tooltip: { trigger: 'axis' },
    legend: { data: ['I_R', 'I_Y', 'I_B'], top: '0%' },
    xAxis: { type: 'category', data: timestamps, axisLabel: { color: '#64748b' } },
    yAxis: { type: 'value', name: 'Current (A)', axisLabel: { color: '#64748b' } },
    series: [
      { name: 'I_R', type: 'line', data: currR, smooth: true, showSymbol: false, lineStyle: { color: '#f43f5e', width: 2 } },
      { name: 'I_Y', type: 'line', data: currY, smooth: true, showSymbol: false, lineStyle: { color: '#f59e0b', width: 2 } },
      { name: 'I_B', type: 'line', data: currB, smooth: true, showSymbol: false, lineStyle: { color: '#3b82f6', width: 2 } },
    ],
    grid: { left: '4%', right: '4%', top: '15%', bottom: '15%', containLabel: true }
  }

  const voltageChart = {
    animation: false,
    tooltip: { trigger: 'axis' },
    legend: { data: ['V_R', 'V_Y', 'V_B'], top: '0%' },
    xAxis: { type: 'category', data: timestamps, axisLabel: { color: '#64748b' } },
    yAxis: { type: 'value', name: 'Voltage (V)', scale: true, axisLabel: { color: '#64748b' } },
    series: [
      { name: 'V_R', type: 'line', data: voltR, smooth: true, showSymbol: false, lineStyle: { color: '#f43f5e', width: 2 } },
      { name: 'V_Y', type: 'line', data: voltY, smooth: true, showSymbol: false, lineStyle: { color: '#f59e0b', width: 2 } },
      { name: 'V_B', type: 'line', data: voltB, smooth: true, showSymbol: false, lineStyle: { color: '#3b82f6', width: 2 } },
    ],
    grid: { left: '4%', right: '4%', top: '15%', bottom: '15%', containLabel: true }
  }

  const watts_total = Number(latest.watts_total ?? ((latest.active_power_kw || 0) * 1000));
  const va_total = Number(latest.va_total ?? (watts_total / (latest.pf_avg || 0.95)));
  const v_ln_avg = Number(latest.v_ln_avg ?? (latest.voltage_v ?? 230));
  const v_ll_avg = Number(latest.v_ll_avg ?? (v_ln_avg * 1.73205));
  const current_total = Number(latest.current_total ?? (latest.current_a ?? 0));
  const pf_avg = Number(latest.pf_avg ?? (latest.power_factor ?? 0.95));
  const frequency = Number(latest.frequency ?? (latest.frequency_hz ?? 50.0));
  const energy_wh = Number(latest.energy_wh ?? ((latest.energy_kwh || 0) * 1000));
  const energy_vah = Number(latest.energy_vah ?? (energy_wh / pf_avg));
  const load_hours = Number(latest.load_hours ?? 1420);

  const memoryMapRegisters = [
    { addr: "40101", param: "Watts Total", val: `${watts_total.toFixed(1)} W`, type: "float" },
    { addr: "40103", param: "Watts R phase", val: `${Number(latest.watts_r ?? watts_total / 3).toFixed(1)} W`, type: "float" },
    { addr: "40105", param: "Watts Y phase", val: `${Number(latest.watts_y ?? watts_total / 3).toFixed(1)} W`, type: "float" },
    { addr: "40107", param: "Watts B phase", val: `${Number(latest.watts_b ?? watts_total / 3).toFixed(1)} W`, type: "float" },
    { addr: "40117", param: "PF Avg (inst)", val: pf_avg.toFixed(3), type: "float" },
    { addr: "40119", param: "PF R phase", val: Number(latest.pf_r ?? pf_avg).toFixed(3), type: "float" },
    { addr: "40121", param: "PF Y phase", val: Number(latest.pf_y ?? pf_avg).toFixed(3), type: "float" },
    { addr: "40123", param: "PF B phase", val: Number(latest.pf_b ?? pf_avg).toFixed(3), type: "float" },
    { addr: "40125", param: "VA total", val: `${va_total.toFixed(1)} VA`, type: "float" },
    { addr: "40127", param: "VA R phase", val: `${Number(latest.va_r ?? va_total / 3).toFixed(1)} VA`, type: "float" },
    { addr: "40129", param: "VA Y phase", val: `${Number(latest.va_y ?? va_total / 3).toFixed(1)} VA`, type: "float" },
    { addr: "40131", param: "VA B phase", val: `${Number(latest.va_b ?? va_total / 3).toFixed(1)} VA`, type: "float" },
    { addr: "40133", param: "VL L average", val: `${v_ll_avg.toFixed(1)} V`, type: "float" },
    { addr: "40135", param: "VR Y phase", val: `${Number(latest.v_ry ?? v_ll_avg).toFixed(1)} V`, type: "float" },
    { addr: "40137", param: "VY B phase", val: `${Number(latest.v_yb ?? v_ll_avg).toFixed(1)} V`, type: "float" },
    { addr: "40139", param: "VB R phase", val: `${Number(latest.v_br ?? v_ll_avg).toFixed(1)} V`, type: "float" },
    { addr: "40141", param: "VL N average", val: `${v_ln_avg.toFixed(1)} V`, type: "float" },
    { addr: "40143", param: "V R phase", val: `${Number(latest.v_r ?? v_ln_avg).toFixed(1)} V`, type: "float" },
    { addr: "40145", param: "V Y phase", val: `${Number(latest.v_y ?? v_ln_avg).toFixed(1)} V`, type: "float" },
    { addr: "40147", param: "V B phase", val: `${Number(latest.v_b ?? v_ln_avg).toFixed(1)} V`, type: "float" },
    { addr: "40149", param: "Current Total", val: `${current_total.toFixed(2)} A`, type: "float" },
    { addr: "40151", param: "Current R phase", val: `${Number(latest.current_r ?? current_total / 3).toFixed(2)} A`, type: "float" },
    { addr: "40153", param: "Current Y phase", val: `${Number(latest.current_y ?? current_total / 3).toFixed(2)} A`, type: "float" },
    { addr: "40155", param: "Current B phase", val: `${Number(latest.current_b ?? current_total / 3).toFixed(2)} A`, type: "float" },
    { addr: "40157", param: "Frequency", val: `${frequency.toFixed(2)} Hz`, type: "float" },
    { addr: "40159", param: "Wh", val: `${energy_wh.toFixed(1)} Wh`, type: "float" },
    { addr: "40161", param: "VAh", val: `${energy_vah.toFixed(1)} VAh`, type: "float" },
    { addr: "40217", param: "Load Hours", val: `${load_hours} hrs`, type: "Unsigned long" }
  ];

  return (
    <div className="max-w-[1600px] mx-auto space-y-6 font-mono text-slate-800 pb-20 p-6">
      
      {/* HEADER */}
      <div className="flex justify-between items-end border-b border-slate-300 pb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="bg-teal-700 text-white text-[11px] font-bold px-2 py-0.5 rounded uppercase tracking-wider">Modbus RTU Engine</span>
            <span className="bg-slate-200 text-slate-700 text-[11px] font-bold px-2 py-0.5 rounded uppercase tracking-wider">27 Parameter Memory Map</span>
          </div>
          <h1 className="text-3xl lg:text-4xl font-extrabold tracking-tight text-slate-800 uppercase">Hardware Telemetry Ledger</h1>
          <p className="text-xs font-semibold tracking-widest text-slate-500 uppercase mt-1">Raw Modbus Register Stream & Industrial Timeseries</p>
        </div>
        <div className="flex gap-2">
           <button 
             onClick={() => setViewMode('log')} 
             className={`px-3 py-1.5 rounded text-xs font-bold uppercase tracking-wider ${viewMode === 'log' ? 'bg-teal-700 text-white shadow-sm' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
           >
             Telemetry Log
           </button>
           <button 
             onClick={() => setViewMode('memory_map')} 
             className={`px-3 py-1.5 rounded text-xs font-bold uppercase tracking-wider ${viewMode === 'memory_map' ? 'bg-teal-700 text-white shadow-sm' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
           >
             Memory Map (40101-40217)
           </button>
        </div>
      </div>

      {/* METRIC RIBBON */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
         <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl shadow-sm">
            <div className="text-[10px] font-semibold uppercase text-slate-500 tracking-widest mb-0.5">Watts Total (40101)</div>
            <div className="text-xl font-bold tracking-tight text-teal-700">{watts_total.toFixed(1)} W</div>
            <div className="text-[10px] text-slate-400">{(watts_total / 1000).toFixed(3)} kW</div>
         </div>
         <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl shadow-sm">
            <div className="text-[10px] font-semibold uppercase text-slate-500 tracking-widest mb-0.5">VA Total (40125)</div>
            <div className="text-xl font-bold tracking-tight text-slate-800">{va_total.toFixed(1)} VA</div>
            <div className="text-[10px] text-slate-400">{(va_total / 1000).toFixed(3)} kVA</div>
         </div>
         <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl shadow-sm">
            <div className="text-[10px] font-semibold uppercase text-slate-500 tracking-widest mb-0.5">VL-N Avg (40141)</div>
            <div className="text-xl font-bold tracking-tight text-slate-800">{v_ln_avg.toFixed(1)} V</div>
            <div className="text-[10px] text-slate-400">LL Avg: {v_ll_avg.toFixed(1)} V</div>
         </div>
         <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl shadow-sm">
            <div className="text-[10px] font-semibold uppercase text-slate-500 tracking-widest mb-0.5">Current Total (40149)</div>
            <div className="text-xl font-bold tracking-tight text-slate-800">{current_total.toFixed(2)} A</div>
            <div className="text-[10px] text-slate-400">Phase IR: {Number(latest.current_r || current_total/3).toFixed(1)} A</div>
         </div>
         <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl shadow-sm">
            <div className="text-[10px] font-semibold uppercase text-slate-500 tracking-widest mb-0.5">PF Avg (40117)</div>
            <div className="text-xl font-bold tracking-tight text-slate-800">{pf_avg.toFixed(3)}</div>
            <div className="text-[10px] text-slate-400">Freq: {frequency.toFixed(2)} Hz</div>
         </div>
         <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl shadow-sm">
            <div className="text-[10px] font-semibold uppercase text-slate-500 tracking-widest mb-0.5">Load Hours (40217)</div>
            <div className="text-xl font-bold tracking-tight text-slate-800">{load_hours} hrs</div>
            <div className="text-[10px] text-slate-400">{data.count} Packets Stored</div>
         </div>
      </div>

      {/* 3-PHASE TIME SERIES CHARTS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
         <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <div className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-3 border-b border-slate-100 pb-2">3-Phase Current Waveforms (IR, IY, IB)</div>
            <ReactECharts option={currentChart} style={{ height: '260px' }} />
         </div>
         <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <div className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-3 border-b border-slate-100 pb-2">3-Phase Voltage Waveforms (VR, VY, VB)</div>
            <ReactECharts option={voltageChart} style={{ height: '260px' }} />
         </div>
      </div>

      {/* VIEW: MEMORY MAP TABLE */}
      {viewMode === 'memory_map' ? (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
           <div className="p-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
              <h2 className="text-xs font-bold uppercase tracking-widest text-slate-700">Memory Map (Addresses 40101 to 40217)</h2>
              <span className="text-xs font-bold text-teal-700">Active Real-Time Register Values</span>
           </div>
           <div className="overflow-x-auto">
             <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-100 border-b border-slate-200 text-slate-600 uppercase tracking-widest font-semibold">
                   <tr>
                      <th className="p-3">Address</th>
                      <th className="p-3">Parameter Name</th>
                      <th className="p-3">Data Type</th>
                      <th className="p-3">Live Value</th>
                      <th className="p-3">Status</th>
                   </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                   {memoryMapRegisters.map(r => (
                      <tr key={r.addr} className="hover:bg-slate-50">
                         <td className="p-3 font-bold text-teal-800">{r.addr}</td>
                         <td className="p-3 font-bold text-slate-800">{r.param}</td>
                         <td className="p-3 text-slate-500">{r.type}</td>
                         <td className="p-3 font-black text-slate-900 bg-slate-50/50">{r.val}</td>
                         <td className="p-3 text-emerald-600 font-bold">ONLINE</td>
                      </tr>
                   ))}
                </tbody>
             </table>
           </div>
        </div>
      ) : (
        /* VIEW: RAW TELEMETRY LOG */
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
           <div className="p-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
              <h2 className="text-xs font-bold uppercase tracking-widest text-slate-700">Historical Telemetry Ingestion Log (Latest 15)</h2>
              <span className="text-xs font-bold text-slate-500">Auto-updating every 1.5s</span>
           </div>
           <div className="overflow-x-auto">
             <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-100 border-b border-slate-200 text-slate-600 uppercase tracking-widest font-semibold">
                   <tr>
                      <th className="p-3">Time</th>
                      <th className="p-3">Watts Total</th>
                      <th className="p-3">Watts (R / Y / B)</th>
                      <th className="p-3">VA Total</th>
                      <th className="p-3">V_LN (R / Y / B)</th>
                      <th className="p-3">I (R / Y / B)</th>
                      <th className="p-3">PF Avg</th>
                      <th className="p-3">Freq</th>
                      <th className="p-3">Wh / VAh</th>
                      <th className="p-3">Hours</th>
                   </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                   {[...history].reverse().slice(0, 15).map((r: any, i: number) => {
                      const wt = Number(r.watts_total ?? ((r.active_power_kw || 0) * 1000));
                      const vat = Number(r.va_total ?? (wt / (r.pf_avg || 0.95)));
                      return (
                        <tr key={i} className="hover:bg-slate-50">
                           <td className="p-3 text-slate-500">{new Date(r.timestamp).toLocaleTimeString()}</td>
                           <td className="p-3 font-bold text-teal-700">{wt.toFixed(0)} W</td>
                           <td className="p-3 text-slate-700">
                              {Number(r.watts_r || wt/3).toFixed(0)} / {Number(r.watts_y || wt/3).toFixed(0)} / {Number(r.watts_b || wt/3).toFixed(0)}
                           </td>
                           <td className="p-3 font-bold text-slate-800">{vat.toFixed(0)} VA</td>
                           <td className="p-3 text-slate-700">
                              {Number(r.v_r || r.voltage_v || 230).toFixed(1)} / {Number(r.v_y || r.voltage_v || 230).toFixed(1)} / {Number(r.v_b || r.voltage_v || 230).toFixed(1)}
                           </td>
                           <td className="p-3 text-slate-700">
                              {Number(r.current_r || (r.current_a||0)/3).toFixed(2)} / {Number(r.current_y || (r.current_a||0)/3).toFixed(2)} / {Number(r.current_b || (r.current_a||0)/3).toFixed(2)}
                           </td>
                           <td className="p-3 font-bold text-slate-800">{Number(r.pf_avg || r.power_factor || 0.95).toFixed(3)}</td>
                           <td className="p-3 text-slate-700">{Number(r.frequency || r.frequency_hz || 50).toFixed(2)} Hz</td>
                           <td className="p-3 text-slate-700">
                              {Number(r.energy_wh || (r.energy_kwh||0)*1000).toFixed(0)} / {Number(r.energy_vah || (r.energy_kwh||0)*1050).toFixed(0)}
                           </td>
                           <td className="p-3 font-bold text-slate-800">{r.load_hours ?? 1420}</td>
                        </tr>
                      );
                   })}
                </tbody>
             </table>
           </div>
        </div>
      )}

    </div>
  )
}
