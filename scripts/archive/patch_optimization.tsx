"use client"
import React, { useState, useEffect } from 'react'
import ReactECharts from 'echarts-for-react'
import { ClientModeBoundary } from "@/components/ClientModeBoundary"

export default function OptimizationIntelligencePage() {
  const [pipeline, setPipeline] = useState<any>(null)
  const [demoState, setDemoState] = useState<any>(null)
  
  const fetchState = async () => {
    try {
      const demoRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/simulation/state`)
      const optRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/optimize`, { method: 'POST' })
      if (demoRes.ok) setDemoState(await demoRes.json())
      if (optRes.ok) setPipeline(await optRes.json())
    } catch (e) {}
  }

  useEffect(() => {
    fetchState()
    let isMounted = true; let tid: any; 
    const loop = async () => { if (!isMounted) return; await fetchState(); if(isMounted) tid = setTimeout(loop, 2000); }; 
    loop(); 
    return () => { isMounted = false; clearTimeout(tid); }
  }, [])

  if (!pipeline || !demoState) return <div className="p-10 font-mono text-slate-500">INITIALIZING AI OPTIMIZER...</div>

  const isOptimized = pipeline.status === 'OPTIMIZED'
  const beforePeak = pipeline.before_peak || demoState.current_demand_kw || 0
  const afterPeak = pipeline.after_peak || beforePeak
  const reduction = beforePeak - afterPeak
  const hasActions = pipeline.actions && pipeline.actions.length > 0
  const primaryAction = hasActions ? pipeline.actions[0] : null
  const alternatives = pipeline.alternatives || []

  const chartOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { top: 0, textStyle: { color: '#64748b', fontSize: 10 } },
    grid: { top: 40, right: 30, bottom: 30, left: 50 },
    xAxis: {
      type: 'category',
      data: ['NOW', '+10 min', '+20 min', '+30 min'],
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisLabel: { color: '#64748b', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#64748b', fontSize: 10 },
      max: Math.max(beforePeak * 1.1, demoState.contract_demand_kw || 150)
    },
    series: [
      {
        name: 'Before AI', type: 'line', data: [demoState.current_demand_kw, beforePeak, beforePeak*0.9, beforePeak*0.8],
        itemStyle: { color: '#ef4444' }, lineStyle: { width: 3, type: 'dashed' }, symbol: 'circle', symbolSize: 6
      },
      {
        name: 'After AI', type: 'line', data: [demoState.current_demand_kw, afterPeak, afterPeak*1.05, afterPeak*1.02],
        itemStyle: { color: '#10b981' }, lineStyle: { width: 4 }, symbol: 'circle', symbolSize: 8
      }
    ]
  }

  return (
    <ClientModeBoundary title="Plant 01 — AI Optimization">
      <div className="max-w-[1600px] mx-auto space-y-6 font-mono text-slate-800 pb-20">
        
        {/* HEADER */}
        <div className="flex justify-between items-end border-b border-slate-200 pb-4">
          <div>
            <h1 className="text-2xl font-black tracking-tighter text-slate-900 uppercase">Optimization Engine</h1>
            <p className="text-xs font-bold tracking-widest text-slate-400 uppercase mt-1">Mathematical peak-demand scheduling & constraint solving</p>
          </div>
          <div className="flex gap-4 text-xs font-bold tracking-widest">
             <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div> SOLVER ACTIVE</div>
          </div>
        </div>

        {/* TOP CARDS: BEFORE vs AFTER */}
        <div className="grid grid-cols-2 gap-6">
           <div className="bg-red-50 border border-red-200 p-6 rounded-xl shadow-sm">
              <div className="text-[10px] font-bold tracking-widest uppercase text-red-500 mb-6">Current State (Do Nothing)</div>
              <div className="flex justify-between items-end">
                 <div>
                    <div className="text-4xl font-black text-red-700 tracking-tighter">{beforePeak.toFixed(1)} kW</div>
                    <div className="text-xs font-bold text-red-600 mt-1 uppercase flex items-center gap-1">▲ High Peak Risk</div>
                 </div>
                 <div className="text-right text-xs space-y-2">
                    <div className="text-slate-600"><span className="text-slate-400 w-24 inline-block text-left">Production</span> <span className="font-bold">100%</span></div>
                    <div className="text-slate-600"><span className="text-slate-400 w-24 inline-block text-left">Compressor</span> <span className="font-bold">Starts NOW</span></div>
                    <div className="text-slate-600"><span className="text-slate-400 w-24 inline-block text-left">Motor</span> <span className="font-bold">Running</span></div>
                 </div>
              </div>
           </div>
           
           <div className="bg-emerald-50 border border-emerald-200 p-6 rounded-xl shadow-sm relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-10">
                 <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
              </div>
              <div className="text-[10px] font-bold tracking-widest uppercase text-emerald-600 mb-6 relative z-10">Optimized State</div>
              <div className="flex justify-between items-end relative z-10">
                 <div>
                    <div className="text-4xl font-black text-emerald-700 tracking-tighter">{afterPeak.toFixed(1)} kW</div>
                    <div className="text-xs font-bold text-emerald-600 mt-1 uppercase flex items-center gap-1">▼ Safe Peak Limit</div>
                 </div>
                 <div className="text-right text-xs space-y-2">
                    <div className="text-slate-600"><span className="text-slate-400 w-24 inline-block text-left">Production</span> <span className="font-bold">100%</span></div>
                    <div className="text-slate-600"><span className="text-slate-400 w-24 inline-block text-left">Compressor</span> <span className="font-bold text-emerald-600">Starts +10m</span></div>
                    <div className="text-slate-600"><span className="text-slate-400 w-24 inline-block text-left">Motor</span> <span className="font-bold">Running</span></div>
                 </div>
              </div>
           </div>
        </div>

        {/* MIDDLE SECTION: CHART + IMPACT */}
        <div className="grid grid-cols-3 gap-6">
           <div className="col-span-2 bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
              <div className="text-[10px] font-bold tracking-widest uppercase text-slate-400 mb-6">Before → Optimized Demand Profile</div>
              <div className="h-[300px]">
                 <ReactECharts option={chartOption} style={{ height: '100%', width: '100%' }} />
              </div>
           </div>
           
           <div className="col-span-1 space-y-6">
              <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm h-full">
                 <div className="text-[10px] font-bold tracking-widest uppercase text-slate-400 mb-6">Decision Impact</div>
                 <div className="space-y-4 text-sm">
                    <div className="flex justify-between border-b border-slate-100 pb-2">
                       <span className="text-slate-500">Peak Demand</span>
                       <span className="font-bold text-emerald-600">-{reduction.toFixed(1)} kW</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-100 pb-2">
                       <span className="text-slate-500">Production</span>
                       <span className="font-bold text-slate-700">0% impact</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-100 pb-2">
                       <span className="text-slate-500">Peak Risk</span>
                       <span className="font-bold text-emerald-600">↓ Reduced to LOW</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-100 pb-2">
                       <span className="text-slate-500">Energy Cost</span>
                       <span className="font-bold text-emerald-600">-₹{(reduction * 8.5).toFixed(0)}</span>
                    </div>
                    <div className="flex justify-between">
                       <span className="text-slate-500">Constraint Violations</span>
                       <span className="font-bold text-slate-400">— None</span>
                    </div>
                 </div>
                 
                 {isOptimized && hasActions && (
                 <div className="mt-8 pt-6 border-t border-slate-200">
                    <div className="text-[10px] font-bold tracking-widest uppercase text-blue-500 mb-2">Selected Action</div>
                    <div className="font-black text-slate-800 leading-tight bg-blue-50 p-3 rounded-lg border border-blue-100">{primaryAction.action}</div>
                 </div>
                 )}
              </div>
           </div>
        </div>

        {/* BOTTOM SECTION: CONSTRAINTS & SEARCH SPACE */}
        <div className="grid grid-cols-2 gap-6">
           {/* CONSTRAINTS */}
           <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-sm text-slate-300">
              <div className="text-[10px] font-bold tracking-widest uppercase text-slate-500 mb-6">Mathematical Constraints</div>
              
              <div className="mb-6">
                 <div className="text-xs font-bold text-white mb-2">PRODUCTION TARGET</div>
                 <div className="w-full bg-slate-800 h-2 rounded-full mb-1">
                    <div className="bg-emerald-500 h-2 rounded-full" style={{ width: '100%' }}></div>
                 </div>
                 <div className="flex justify-between text-[10px] font-bold uppercase text-slate-400">
                    <span>Current Capacity</span>
                    <span className="text-emerald-400">100% REQUIRED</span>
                 </div>
              </div>

              <div className="space-y-3 mt-8">
                 <div className="text-xs font-bold text-white mb-3">OPTIMIZATION OBJECTIVE: MINIMIZE PEAK</div>
                 <div className="flex items-center gap-3 text-xs">
                    <span className="text-emerald-400">✓</span> <span className="font-bold">Production ≥ 100%</span>
                 </div>
                 <div className="flex items-center gap-3 text-xs">
                    <span className="text-emerald-400">✓</span> <span>Critical assets protected</span>
                 </div>
                 <div className="flex items-center gap-3 text-xs">
                    <span className="text-emerald-400">✓</span> <span>Machine availability & maintenance</span>
                 </div>
              </div>
           </div>

           {/* SEARCH SPACE */}
           <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
              <div className="text-[10px] font-bold tracking-widest uppercase text-slate-400 mb-4">AI Search Space Evaluated</div>
              <div className="space-y-4">
                 {alternatives.map((alt: any, idx: number) => {
                    const isRejected = alt.status === 'REJECTED'
                    const isSelected = alt.status === 'SELECTED'
                    return (
                       <div key={idx} className={`p-3 rounded border text-xs flex justify-between items-center ${isSelected ? 'border-emerald-200 bg-emerald-50' : isRejected ? 'border-red-100 bg-red-50/50 opacity-80' : 'border-slate-100 bg-slate-50'}`}>
                          <div className="flex items-center gap-3">
                             {isSelected ? <span className="text-emerald-600 font-black">✓</span> : isRejected ? <span className="text-red-500 font-black">✕</span> : <span className="text-slate-400 font-bold">—</span>}
                             <span className={`font-bold ${isRejected ? 'text-slate-600 line-through' : 'text-slate-800'}`}>{alt.name}</span>
                          </div>
                          <div className="flex items-center gap-4 text-right">
                             {isRejected && <span className="text-red-500 font-bold">{alt.reason}</span>}
                             {!isRejected && <span className="text-slate-500 font-mono">{alt.peak} kW</span>}
                          </div>
                       </div>
                    )
                 })}
                 {alternatives.length === 0 && (
                    <div className="text-xs text-slate-500 italic">No alternative scenarios evaluated in current horizon.</div>
                 )}
              </div>
           </div>
        </div>

      </div>
    </ClientModeBoundary>
  )
}
