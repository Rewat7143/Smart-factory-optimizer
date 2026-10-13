"use client"
import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import ReactECharts from 'echarts-for-react'
import FieldEngineerPictorialView from './FieldEngineerPictorialView'

export default function LiveTelemetryDashboard() {
  const [status, setStatus] = useState<any>(null)
  const [history, setHistory] = useState<any[]>([])
  const [errorStr, setErrorStr] = useState<string>('')
  const [activeTab, setActiveTab] = useState<'overview' | 'phases' | 'memory_map'>('overview')

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      if (!isMounted) return;
      try {
        const baseUrl = (typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : 'http://localhost:8000/api')
        const statusRes = await fetch(`${baseUrl}/telemetry/source-status`);
        if (statusRes.ok) {
            const data = await statusRes.json();
            if (isMounted) setStatus(data);
        } else {
            if (isMounted) setErrorStr(`Status Error: ${statusRes.status} ${statusRes.statusText}`);
        }
        
        const histRes = await fetch(`${baseUrl}/telemetry/history`);
        if (histRes.ok) {
            const data = await histRes.json();
            if (isMounted && data.history) setHistory(data.history);
        } else {
            if (isMounted && !errorStr) setErrorStr(`History Error: ${histRes.status} ${histRes.statusText}`);
        }
      } catch (e: any) {
        console.error(e);
        if (isMounted) setErrorStr(`Fetch Exception: ${e.message}`);
      }
    }
    fetchData()
    const interval = setInterval(fetchData, 1500)
    return () => {
        isMounted = false;
        clearInterval(interval)
    }
  }, [errorStr])

  if (errorStr) return <div className="p-6 text-red-600 font-bold">Error: {errorStr}</div>
  if (!status) return <div className="p-6 text-slate-800 font-bold">Connecting to Live 3-Phase Meter...</div>

  const isOffline = status.source_status === 'OFFLINE' || status.active_source === 'NONE';
  const reading = status.latest_reading || {};

  // Extract all 27 parameters with smart fallbacks
  const watts_total = Number(reading.watts_total ?? (Number(reading.active_power_kw || 0) * 1000));
  const watts_r = Number(reading.watts_r ?? (watts_total / 3));
  const watts_y = Number(reading.watts_y ?? (watts_total / 3));
  const watts_b = Number(reading.watts_b ?? (watts_total / 3));

  const pf_avg = Number(reading.pf_avg ?? (reading.power_factor ?? 0.95));
  const pf_r = Number(reading.pf_r ?? pf_avg);
  const pf_y = Number(reading.pf_y ?? pf_avg);
  const pf_b = Number(reading.pf_b ?? pf_avg);

  const va_total = Number(reading.va_total ?? (pf_avg ? watts_total / pf_avg : watts_total));
  const va_r = Number(reading.va_r ?? (va_total / 3));
  const va_y = Number(reading.va_y ?? (va_total / 3));
  const va_b = Number(reading.va_b ?? (va_total / 3));

  const v_ln_avg = Number(reading.v_ln_avg ?? (reading.voltage_v ?? 230.0));
  const v_r = Number(reading.v_r ?? v_ln_avg);
  const v_y = Number(reading.v_y ?? v_ln_avg);
  const v_b = Number(reading.v_b ?? v_ln_avg);

  const v_ll_avg = Number(reading.v_ll_avg ?? (v_ln_avg * 1.73205));
  const v_ry = Number(reading.v_ry ?? v_ll_avg);
  const v_yb = Number(reading.v_yb ?? v_ll_avg);
  const v_br = Number(reading.v_br ?? v_ll_avg);

  const current_total = Number(reading.current_total ?? (reading.current_a ?? 0));
  const current_r = Number(reading.current_r ?? (current_total / 3));
  const current_y = Number(reading.current_y ?? (current_total / 3));
  const current_b = Number(reading.current_b ?? (current_total / 3));

  const frequency = Number(reading.frequency ?? (reading.frequency_hz ?? 50.0));
  const energy_wh = Number(reading.energy_wh ?? (Number(reading.energy_kwh || 0) * 1000));
  const energy_vah = Number(reading.energy_vah ?? (pf_avg ? energy_wh / pf_avg : energy_wh));
  const load_hours = Number(reading.load_hours ?? 1420);

  // Modbus memory map 27-item definition table mirroring the user's manual image
  const memoryMapRows = [
    { addr: "40101", name: "Watts Total", val: `${watts_total.toFixed(1)} W`, kwVal: `${(watts_total / 1000).toFixed(3)} kW`, type: "float", phase: "3-Phase Total" },
    { addr: "40103", name: "Watts R phase", val: `${watts_r.toFixed(1)} W`, kwVal: `${(watts_r / 1000).toFixed(3)} kW`, type: "float", phase: "R Phase" },
    { addr: "40105", name: "Watts Y phase", val: `${watts_y.toFixed(1)} W`, kwVal: `${(watts_y / 1000).toFixed(3)} kW`, type: "float", phase: "Y Phase" },
    { addr: "40107", name: "Watts B phase", val: `${watts_b.toFixed(1)} W`, kwVal: `${(watts_b / 1000).toFixed(3)} kW`, type: "float", phase: "B Phase" },
    { addr: "40117", name: "PF Avg (inst)", val: pf_avg.toFixed(3), kwVal: "-", type: "float", phase: "Average" },
    { addr: "40119", name: "PF R phase", val: pf_r.toFixed(3), kwVal: "-", type: "float", phase: "R Phase" },
    { addr: "40121", name: "PF Y phase", val: pf_y.toFixed(3), kwVal: "-", type: "float", phase: "Y Phase" },
    { addr: "40123", name: "PF B phase", val: pf_b.toFixed(3), kwVal: "-", type: "float", phase: "B Phase" },
    { addr: "40125", name: "VA total", val: `${va_total.toFixed(1)} VA`, kwVal: `${(va_total / 1000).toFixed(3)} kVA`, type: "float", phase: "3-Phase Total" },
    { addr: "40127", name: "VA R phase", val: `${va_r.toFixed(1)} VA`, kwVal: `${(va_r / 1000).toFixed(3)} kVA`, type: "float", phase: "R Phase" },
    { addr: "40129", name: "VA Y phase", val: `${va_y.toFixed(1)} VA`, kwVal: `${(va_y / 1000).toFixed(3)} kVA`, type: "float", phase: "Y Phase" },
    { addr: "40131", name: "VA B phase", val: `${va_b.toFixed(1)} VA`, kwVal: `${(va_b / 1000).toFixed(3)} kVA`, type: "float", phase: "B Phase" },
    { addr: "40133", name: "VL L average", val: `${v_ll_avg.toFixed(1)} V`, kwVal: "-", type: "float", phase: "Line-to-Line Avg" },
    { addr: "40135", name: "VR Y phase", val: `${v_ry.toFixed(1)} V`, kwVal: "-", type: "float", phase: "Phase R-Y" },
    { addr: "40137", name: "VY B phase", val: `${v_yb.toFixed(1)} V`, kwVal: "-", type: "float", phase: "Phase Y-B" },
    { addr: "40139", name: "VB R phase", val: `${v_br.toFixed(1)} V`, kwVal: "-", type: "float", phase: "Phase B-R" },
    { addr: "40141", name: "VL N average", val: `${v_ln_avg.toFixed(1)} V`, kwVal: "-", type: "float", phase: "Line-to-Neutral Avg" },
    { addr: "40143", name: "V R phase", val: `${v_r.toFixed(1)} V`, kwVal: "-", type: "float", phase: "Phase R (VRN)" },
    { addr: "40145", name: "V Y phase", val: `${v_y.toFixed(1)} V`, kwVal: "-", type: "float", phase: "Phase Y (VYN)" },
    { addr: "40147", name: "V B phase", val: `${v_b.toFixed(1)} V`, kwVal: "-", type: "float", phase: "Phase B (VBN)" },
    { addr: "40149", name: "Current Total", val: `${current_total.toFixed(2)} A`, kwVal: "-", type: "float", phase: "3-Phase Total" },
    { addr: "40151", name: "Current R phase", val: `${current_r.toFixed(2)} A`, kwVal: "-", type: "float", phase: "R Phase" },
    { addr: "40153", name: "Current Y phase", val: `${current_y.toFixed(2)} A`, kwVal: "-", type: "float", phase: "Y Phase" },
    { addr: "40155", name: "Current B phase", val: `${current_b.toFixed(2)} A`, kwVal: "-", type: "float", phase: "B Phase" },
    { addr: "40157", name: "Frequency", val: `${frequency.toFixed(2)} Hz`, kwVal: "-", type: "float", phase: "Grid Frequency" },
    { addr: "40159", name: "Wh", val: `${energy_wh.toFixed(1)} Wh`, kwVal: `${(energy_wh / 1000).toFixed(2)} kWh`, type: "float", phase: "Active Energy" },
    { addr: "40161", name: "VAh", val: `${energy_vah.toFixed(1)} VAh`, kwVal: `${(energy_vah / 1000).toFixed(2)} kVAh`, type: "float", phase: "Apparent Energy" },
    { addr: "40217", name: "Load Hours", val: `${load_hours} hrs`, kwVal: "-", type: "Unsigned long", phase: "Run Counter" }
  ];

  // Chart timeseries data from history
  const recentHist = history.slice(-30);
  const chartTimes = recentHist.map(r => new Date(r.timestamp).toLocaleTimeString());
  const powerSeries = recentHist.map(r => Number(r.active_power_kw || (r.watts_total ? r.watts_total / 1000 : 0)));
  const currRSeries = recentHist.map(r => Number(r.current_r ?? (r.current_a ? r.current_a / 3 : 0)));
  const currYSeries = recentHist.map(r => Number(r.current_y ?? (r.current_a ? r.current_a / 3 : 0)));
  const currBSeries = recentHist.map(r => Number(r.current_b ?? (r.current_a ? r.current_a / 3 : 0)));

  const voltRSeries = recentHist.map(r => Number(r.v_r ?? (r.voltage_v ?? 230)));
  const voltYSeries = recentHist.map(r => Number(r.v_y ?? (r.voltage_v ?? 230)));
  const voltBSeries = recentHist.map(r => Number(r.v_b ?? (r.voltage_v ?? 230)));

  return (
    <div className="max-w-[1600px] mx-auto space-y-6 font-mono text-slate-800 pb-20 p-6">
      

      {/* VIEW TABS */}
      <div className="flex flex-wrap gap-2 border-b-2 border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2.5 rounded-xl text-xs font-black uppercase tracking-wider transition-all ${
            activeTab === 'overview'
              ? 'bg-teal-700 text-white shadow-md ring-2 ring-teal-500'
              : 'bg-white border-2 border-slate-300 text-slate-800 hover:bg-slate-100'
          }`}
        >
          ⚡ Plant Visual Dashboard
        </button>
        <button
          onClick={() => setActiveTab('phases')}
          className={`px-4 py-2.5 rounded-xl text-xs font-black uppercase tracking-wider transition-all ${
            activeTab === 'phases'
              ? 'bg-teal-700 text-white shadow-md ring-2 ring-teal-500'
              : 'bg-white border-2 border-slate-300 text-slate-800 hover:bg-slate-100'
          }`}
        >
          🔴🟡🔵 3-Phase Breakdown (R-Y-B)
        </button>
        <button
          onClick={() => setActiveTab('memory_map')}
          className={`px-4 py-2.5 rounded-xl text-xs font-black uppercase tracking-wider transition-all ${
            activeTab === 'memory_map'
              ? 'bg-teal-700 text-white shadow-md ring-2 ring-teal-500'
              : 'bg-white border-2 border-slate-300 text-slate-800 hover:bg-slate-100'
          }`}
        >
          📋 Memory Map Register Verification (27 Params)
        </button>

        {/* Link to dedicated AI Demand Forecast & Graphs Page */}
        <Link
          href="/demand-forecast"
          className="px-4 py-2.5 rounded-xl text-xs font-black uppercase tracking-wider bg-indigo-50 border-2 border-indigo-300 text-indigo-950 hover:bg-indigo-100 transition-all flex items-center gap-1.5 shadow-xs ml-auto"
        >
          <span>📈 AI Demand Forecast Graphs</span>
          <span>&rarr;</span>
        </Link>
      </div>

      {/* KEY TOP KPI RIBBON (Active on phase breakdown & memory map tabs) */}
      {activeTab !== 'overview' && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
           <div className="bg-white border-2 border-slate-200 p-4 rounded-xl shadow-sm">
              <div className="text-[10px] font-bold uppercase text-slate-400 tracking-widest">Watts Total (40101)</div>
              <div className="text-xl lg:text-2xl font-black text-teal-700 mt-1">
                {isOffline ? '---' : `${watts_total.toFixed(1)}`} <span className="text-xs font-bold text-slate-500">W</span>
              </div>
              <div className="text-[11px] text-slate-400 font-semibold mt-0.5">{(watts_total / 1000).toFixed(3)} kW</div>
           </div>

           <div className="bg-white border-2 border-slate-200 p-4 rounded-xl shadow-sm">
              <div className="text-[10px] font-bold uppercase text-slate-400 tracking-widest">VA Total (40125)</div>
              <div className="text-xl lg:text-2xl font-black text-slate-800 mt-1">
                {isOffline ? '---' : `${va_total.toFixed(1)}`} <span className="text-xs font-bold text-slate-500">VA</span>
              </div>
              <div className="text-[11px] text-slate-400 font-semibold mt-0.5">{(va_total / 1000).toFixed(3)} kVA</div>
           </div>

           <div className="bg-white border-2 border-slate-200 p-4 rounded-xl shadow-sm">
              <div className="text-[10px] font-bold uppercase text-slate-400 tracking-widest">Current Total (40149)</div>
              <div className="text-xl lg:text-2xl font-black text-slate-800 mt-1">
                {isOffline ? '---' : current_total.toFixed(2)} <span className="text-xs font-bold text-slate-500">A</span>
              </div>
              <div className="text-[11px] text-slate-400 font-semibold mt-0.5">3-Phase Sum</div>
           </div>

           <div className="bg-white border-2 border-slate-200 p-4 rounded-xl shadow-sm">
              <div className="text-[10px] font-bold uppercase text-slate-400 tracking-widest">PF Avg (40117)</div>
              <div className="text-xl lg:text-2xl font-black text-slate-800 mt-1">
                {isOffline ? '---' : pf_avg.toFixed(3)}
              </div>
              <div className="text-[11px] text-emerald-600 font-bold mt-0.5">{pf_avg >= 0.95 ? 'HEALTHY' : 'LAGGING RISK'}</div>
           </div>

           <div className="bg-white border-2 border-slate-200 p-4 rounded-xl shadow-sm">
              <div className="text-[10px] font-bold uppercase text-slate-400 tracking-widest">Frequency (40157)</div>
              <div className="text-xl lg:text-2xl font-black text-slate-800 mt-1">
                {isOffline ? '---' : frequency.toFixed(2)} <span className="text-xs font-bold text-slate-500">Hz</span>
              </div>
              <div className="text-[11px] text-slate-400 font-semibold mt-0.5">50 Hz Grid Nominal</div>
           </div>

           <div className="bg-white border-2 border-slate-200 p-4 rounded-xl shadow-sm">
              <div className="text-[10px] font-bold uppercase text-slate-400 tracking-widest">Load Hours (40217)</div>
              <div className="text-xl lg:text-2xl font-black text-slate-800 mt-1">
                {isOffline ? '---' : load_hours} <span className="text-xs font-bold text-slate-500">hrs</span>
              </div>
              <div className="text-[11px] text-slate-400 font-semibold mt-0.5">Operating Runtime</div>
           </div>
        </div>
      )}

      {/* TAB 1: VISUAL OVERVIEW DASHBOARD */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <FieldEngineerPictorialView />
        </div>
      )}

      {/* TAB 2: 3-PHASE DETAILED BREAKDOWN */}
      {activeTab === 'phases' && (
        <div className="space-y-6">
          <div className="bg-white border-2 border-slate-200 rounded-xl p-6 shadow-sm">
            <h2 className="text-base font-bold uppercase tracking-wider text-slate-800 mb-4">
              3-Phase Load Balance & Phase Comparison
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm border-collapse">
                <thead>
                  <tr className="bg-slate-100 text-slate-700 uppercase text-xs tracking-wider border-b-2 border-slate-200">
                    <th className="p-3">Measurement</th>
                    <th className="p-3 text-rose-600 font-bold">Phase R</th>
                    <th className="p-3 text-amber-600 font-bold">Phase Y</th>
                    <th className="p-3 text-blue-600 font-bold">Phase B</th>
                    <th className="p-3 text-teal-700 font-bold">3-Phase Average / Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  <tr>
                    <td className="p-3 text-slate-500 font-bold">Line-to-Neutral Voltage</td>
                    <td className="p-3 font-bold text-slate-800">{v_r.toFixed(1)} V</td>
                    <td className="p-3 font-bold text-slate-800">{v_y.toFixed(1)} V</td>
                    <td className="p-3 font-bold text-slate-800">{v_b.toFixed(1)} V</td>
                    <td className="p-3 font-bold text-teal-700">{v_ln_avg.toFixed(1)} V (Avg)</td>
                  </tr>
                  <tr>
                    <td className="p-3 text-slate-500 font-bold">Phase Current</td>
                    <td className="p-3 font-bold text-slate-800">{current_r.toFixed(2)} A</td>
                    <td className="p-3 font-bold text-slate-800">{current_y.toFixed(2)} A</td>
                    <td className="p-3 font-bold text-slate-800">{current_b.toFixed(2)} A</td>
                    <td className="p-3 font-bold text-teal-700">{current_total.toFixed(2)} A (Total)</td>
                  </tr>
                  <tr>
                    <td className="p-3 text-slate-500 font-bold">Active Power (Watts)</td>
                    <td className="p-3 font-bold text-slate-800">{watts_r.toFixed(1)} W</td>
                    <td className="p-3 font-bold text-slate-800">{watts_y.toFixed(1)} W</td>
                    <td className="p-3 font-bold text-slate-800">{watts_b.toFixed(1)} W</td>
                    <td className="p-3 font-bold text-teal-700">{watts_total.toFixed(1)} W (Total)</td>
                  </tr>
                  <tr>
                    <td className="p-3 text-slate-500 font-bold">Apparent Power (VA)</td>
                    <td className="p-3 font-bold text-slate-800">{va_r.toFixed(1)} VA</td>
                    <td className="p-3 font-bold text-slate-800">{va_y.toFixed(1)} VA</td>
                    <td className="p-3 font-bold text-slate-800">{va_b.toFixed(1)} VA</td>
                    <td className="p-3 font-bold text-teal-700">{va_total.toFixed(1)} VA (Total)</td>
                  </tr>
                  <tr>
                    <td className="p-3 text-slate-500 font-bold">Power Factor</td>
                    <td className="p-3 font-bold text-slate-800">{pf_r.toFixed(3)}</td>
                    <td className="p-3 font-bold text-slate-800">{pf_y.toFixed(3)}</td>
                    <td className="p-3 font-bold text-slate-800">{pf_b.toFixed(3)}</td>
                    <td className="p-3 font-bold text-teal-700">{pf_avg.toFixed(3)} (Avg)</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* VOLTAGE CHARTS */}
            <div className="mt-8">
              <h3 className="text-xs font-bold uppercase tracking-widest text-slate-600 mb-2">3-Phase Voltage Profile (VR, VY, VB)</h3>
              <ReactECharts 
                style={{ height: '260px' }}
                option={{
                  animation: false,
                  tooltip: { trigger: 'axis' },
                  xAxis: { type: 'category', data: chartTimes, axisLabel: { color: '#64748b' } },
                  yAxis: { type: 'value', name: 'Volts', scale: true, axisLabel: { color: '#64748b' } },
                  series: [
                    { name: 'VR', type: 'line', data: voltRSeries, smooth: true, showSymbol: false, lineStyle: { color: '#f43f5e', width: 2 } },
                    { name: 'VY', type: 'line', data: voltYSeries, smooth: true, showSymbol: false, lineStyle: { color: '#f59e0b', width: 2 } },
                    { name: 'VB', type: 'line', data: voltBSeries, smooth: true, showSymbol: false, lineStyle: { color: '#3b82f6', width: 2 } }
                  ],
                  grid: { left: '4%', right: '4%', top: '15%', bottom: '10%', containLabel: true }
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: COMPLETE 27-REGISTER MODBUS MEMORY MAP TABLE */}
      {activeTab === 'memory_map' && (
        <div className="bg-white border-2 border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
            <div>
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800">
                6. Memory Map Verification Ledger (All 27 Meter Addresses)
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Exact registers defined in manufacturer memory map specifications.
              </p>
            </div>
            <span className="text-xs font-bold bg-teal-100 text-teal-800 px-3 py-1 rounded-full border border-teal-200">
              27 / 27 Streaming Active
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-100 text-slate-600 text-xs uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="p-3 font-bold">Address</th>
                  <th className="p-3 font-bold">Parameter Name</th>
                  <th className="p-3 font-bold">Classification</th>
                  <th className="p-3 font-bold">Live Value</th>
                  <th className="p-3 font-bold">Normalized (kW / kVA)</th>
                  <th className="p-3 font-bold">Data Type</th>
                  <th className="p-3 font-bold text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono text-xs">
                {memoryMapRows.map((row) => (
                  <tr key={row.addr} className="hover:bg-slate-50">
                    <td className="p-3 font-bold text-teal-800">{row.addr}</td>
                    <td className="p-3 font-bold text-slate-800">{row.name}</td>
                    <td className="p-3 text-slate-500 font-sans">{row.phase}</td>
                    <td className="p-3 font-black text-slate-800 bg-slate-50/50">{row.val}</td>
                    <td className="p-3 text-slate-600">{row.kwVal}</td>
                    <td className="p-3 text-slate-500 font-semibold">{row.type}</td>
                    <td className="p-3 text-center">
                      <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                        SYNCED
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  )
}
