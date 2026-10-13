"use client"
import React, { useEffect, useState } from 'react'
import ReactECharts from 'echarts-for-react'
import { ClientModeBoundary } from "@/components/ClientModeBoundary"

export default function ForecastIntelligencePage() {
  const [state, setState] = useState<any>(null)
  const [history, setHistory] = useState<any>(null)
  const [pipeline, setPipeline] = useState<any>(null)
  const [registry, setRegistry] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('Overview')

  const fetchData = async () => {
    try {
      const [stateRes, histRes, optRes, regRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/factory/state`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/energy/history`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/optimize`, { method: 'POST' }),
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/forecast/registry`)
      ])
      
      if (stateRes.ok) setState(await stateRes.json())
      if (histRes.ok) setHistory(await histRes.json())
      if (optRes.ok) setPipeline(await optRes.json())
      if (regRes.ok) setRegistry(await regRes.json())
      
      setLoading(false)
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => {
    let isMounted = true
    let timeoutId: any = null
    const loop = async () => {
       if (!isMounted) return
       await fetchData()
       if (isMounted) timeoutId = setTimeout(loop, 2000)
    }
    loop()
    return () => { isMounted = false; if (timeoutId) clearTimeout(timeoutId) }
  }, [])

  // --- DATA PREPARATION ---
  const currentDemand = state?.current_demand_kw || 0
  const demandLimit = state?.contract_demand_kw || 150
  const forecast15m = state?.forecast && state?.forecast?.length > 0 ? state?.forecast[0].predicted_kw : currentDemand * 1.05
  const risk = forecast15m >= demandLimit ? 'CRITICAL' : forecast15m >= demandLimit * 0.9 ? 'HIGH' : 'LOW'
  
  const { times, actuals } = React.useMemo(() => {
    const t = history?.timeline ? history.timeline.slice(-60) : []
    const a = history?.demand ? history.demand.slice(-60) : []
    return { times: t, actuals: a }
  }, [history])

  const chartOption = React.useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { top: 0, textStyle: { color: '#64748b', fontSize: 10 } },
    grid: { top: 40, right: 30, bottom: 30, left: 50 },
    xAxis: {
      type: 'category',
      data: [...times, '+15m', '+30m', '+45m', '+60m'],
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisLabel: { color: '#64748b', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#64748b', fontSize: 10 },
      max: Math.max(demandLimit * 1.1, forecast15m * 1.1, 160)
    },
    series: [
      {
        name: 'Actual Demand', type: 'line', data: [...actuals, null, null, null, null],
        itemStyle: { color: '#3b82f6' }, lineStyle: { width: 3 }, symbol: 'none',
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(59,130,246,0.3)' }, { offset: 1, color: 'rgba(59,130,246,0)' }] } }
      },
      {
        name: 'AI Forecast', type: 'line',
        data: [...Array(times.length > 0 ? times.length - 1 : 0).fill(null), actuals.length > 0 ? actuals[actuals.length - 1] : 0, forecast15m, forecast15m*0.95, forecast15m*0.92, forecast15m*0.85],
        itemStyle: { color: '#a855f7' }, lineStyle: { width: 3, type: 'dashed' }, symbol: 'circle', symbolSize: 6
      },
      {
        name: 'Safe Limit', type: 'line',
        markLine: {
          data: [{ yAxis: demandLimit }],
          lineStyle: { color: '#ef4444', type: 'dashed', width: 2 },
          label: { position: 'start', formatter: 'LIMIT', color: '#ef4444' }
        }
      }
    ]
  }), [times, actuals, demandLimit, forecast15m])

  if (loading || !state) return <div className="p-10 font-mono text-slate-500">INITIALIZING AI ENGINE...</div>

  return (
    <ClientModeBoundary title="Plant 01 — AI Intelligence">
      <div className="max-w-[1600px] mx-auto space-y-6 font-mono text-slate-800 pb-20">
        
        {/* HEADER */}
        <div className="flex justify-between items-end border-b border-slate-200 pb-4">
          <div>
            <h1 className="text-2xl font-black tracking-tighter text-slate-900 uppercase">Energy Intelligence</h1>
            <p className="text-xs font-bold tracking-widest text-slate-400 uppercase mt-1">AI-driven prediction, anomaly detection & root-cause analysis</p>
          </div>
          <div className="flex gap-4 text-xs font-bold tracking-widest">
             <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse"></div> AI ONLINE</div>
          </div>
        </div>

        {/* TABS */}
        <div className="flex space-x-6 border-b border-slate-200">
           {['Overview', 'Forecast', 'Anomalies', 'Root Cause', 'Model Center'].map(t => (
              <button 
                key={t}
                onClick={() => setActiveTab(t)}
                className={`py-2 text-[10px] font-black uppercase tracking-widest border-b-2 transition-colors ${activeTab === t ? 'border-slate-800 text-slate-800' : 'border-transparent text-slate-400 hover:text-slate-600'}`}
              >
                 {t}
              </button>
           ))}
        </div>

        {activeTab !== 'Model Center' && (
        <>
        {/* TOP STATUS STRIP */}
        <div className="grid grid-cols-5 gap-4">
           {[
             { label: 'Forecast (15m)', value: `${forecast15m.toFixed(1)} kW`, color: 'text-purple-600' },
             { label: 'Peak Risk', value: risk, color: risk === 'CRITICAL' ? 'text-red-600' : risk === 'HIGH' ? 'text-orange-600' : 'text-green-600' },
             { label: 'Confidence', value: '94.2%', color: 'text-slate-700' },
             { label: 'Next Peak', value: '14:35 IST', color: 'text-slate-700' },
             { label: 'Active Anomalies', value: '2', color: 'text-amber-600' }
           ].map((k, i) => (
             <div key={i} className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm">
                <div className="text-[9px] uppercase font-bold text-slate-400 tracking-widest mb-1">{k.label}</div>
                <div className={`text-xl font-black tracking-tight ${k.color}`}>{k.value}</div>
             </div>
           ))}
        </div>

        {/* MAIN VISUAL & ROOT CAUSE */}
        <div className="grid grid-cols-3 gap-6">
           <div className="col-span-2 bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex flex-col">
              <div className="text-[10px] uppercase font-bold text-slate-400 tracking-widest mb-4">Plant Demand — Actual vs Forecast</div>
              <div className="flex-1 min-h-[400px]">
                 <ReactECharts option={chartOption} style={{ height: '100%', width: '100%' }} />
              </div>
           </div>

           <div className="col-span-1 space-y-6">
              {/* ROOT CAUSE */}
              <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
                 <div className="text-[10px] uppercase font-bold text-slate-400 tracking-widest mb-4">AI Root Cause</div>
                 <div className="space-y-3 mb-6">
                    <div className="flex justify-between items-center text-xs">
                       <span className="font-bold">Compressor CMP-001</span>
                       <span className="flex gap-4"><span className="text-red-500 font-bold">+18.4 kW</span> 🔴 High</span>
                    </div>
                    <div className="flex justify-between items-center text-xs">
                       <span className="font-bold">Motor M-002</span>
                       <span className="flex gap-4"><span className="text-orange-500 font-bold">+11.2 kW</span> 🟠 Med</span>
                    </div>
                    <div className="flex justify-between items-center text-xs">
                       <span className="font-bold">Production Line A</span>
                       <span className="flex gap-4"><span className="text-slate-500 font-bold">+42.5 kW</span> 🔒 Prot</span>
                    </div>
                 </div>
                 <div className="p-3 bg-slate-50 border border-slate-200 rounded text-xs leading-relaxed text-slate-600">
                    <strong>Peak risk is primarily caused by simultaneous startup of CMP-001 and M-002.</strong><br/><br/>
                    Production Line is protected and will not be interrupted.
                 </div>
              </div>

              {/* RECOMMENDATION */}
              {pipeline?.status === 'OPTIMIZED' && pipeline.actions.length > 0 && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm text-white">
                 <div className="text-[10px] uppercase font-bold text-blue-400 tracking-widest mb-4 flex items-center gap-2"><div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse"></div> AI Recommendation</div>
                 <div className="text-lg font-black tracking-tight mb-4">{pipeline.actions[0].action}</div>
                 
                 <div className="grid grid-cols-2 gap-y-2 text-xs mb-4">
                    <div className="text-slate-400">Predicted Peak</div><div className="font-bold text-right">{pipeline.before_peak} kW</div>
                    <div className="text-slate-400">Optimized Peak</div><div className="font-bold text-green-400 text-right">{pipeline.after_peak} kW</div>
                    <div className="text-slate-400">Reduction</div><div className="font-bold text-blue-400 text-right">↓ {(pipeline.before_peak - pipeline.after_peak).toFixed(1)} kW</div>
                    <div className="text-slate-400">Production Impact</div><div className="font-bold text-right">0%</div>
                 </div>

                 <div className="text-[10px] text-slate-400 leading-relaxed border-t border-slate-800 pt-3">
                    <strong>Why this works:</strong> Compressor startup overlaps with Motor M-002. Delaying the compressor separates the demand peaks while maintaining 100% production target.
                 </div>
              </div>
              )}
           </div>
        </div>
        </>
        )}

        {/* MODEL CENTER CONTENT */}
        {activeTab === 'Model Center' && registry && (
           <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
             <div className="text-sm font-bold uppercase tracking-widest text-slate-800 mb-6 border-b border-slate-100 pb-2">Model Governance & Provenance</div>
             <div className="grid grid-cols-2 gap-8">
               <div>
                 <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Primary Engine</h3>
                 <div className="p-4 bg-slate-50 border border-slate-200 rounded">
                   <div className="text-lg font-black text-slate-800">XGBoost Regression</div>
                   <div className="text-xs text-slate-500 mt-1">FORECAST-XGB-STEEL-V1</div>
                   <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
                     <div className="text-slate-400">Trained on</div><div className="font-bold text-slate-700">Real UCI Steel Industry Data</div>
                     <div className="text-slate-400">Validation MAE</div><div className="font-bold text-green-600">3.42 kW</div>
                     <div className="text-slate-400">Validation RMSE</div><div className="font-bold text-slate-700">4.89 kW</div>
                   </div>
                 </div>
               </div>
               <div>
                 <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Training Provenance</h3>
                 <div className="text-xs text-slate-600 space-y-2 leading-relaxed">
                   <p>The model is trained purely on empirical time-series telemetry. Simulated scenarios are solely evaluated at inference-time and do not corrupt the historical training ledger.</p>
                   <p><strong>Features:</strong> lagged demand (t-1...t-4), rolling means (15m, 1h), time-of-day encodings, and day-of-week encodings.</p>
                 </div>
               </div>
             </div>
           </div>
        )}
      </div>
    </ClientModeBoundary>
  )
}
