"use client"
import React, { useEffect, useState } from 'react'
import ReactECharts from 'echarts-for-react'

export default function EnergyIntelligencePage() {
  const [history, setHistory] = useState<any>(null)

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(`${(typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))}/energy/history`)
        if (res.ok) setHistory(await res.json())
      } catch (e) {}
    }
    fetchHistory()
  }, [])

  if (!history) return <div className="text-slate-800 p-10 font-mono">LOADING HISTORICAL INTELLIGENCE...</div>

  const demandOption = {
    title: { text: 'Demand Profile (7 Days)', textStyle: { fontSize: 12, fontWeight: 'bold', color: '#64748b' } },
    tooltip: { trigger: 'axis' },
    legend: { data: ['Actual Demand', 'Safe Target', 'Contract Demand'], bottom: 0, textStyle: {fontSize: 10} },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '15%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: history.timeline },
    yAxis: { type: 'value', name: 'kW' },
    series: [
      { name: 'Actual Demand', type: 'line', data: history.demand, itemStyle: { color: '#0ea5e9' }, areaStyle: { color: 'rgba(14, 165, 233, 0.1)' } },
      { name: 'Safe Target', type: 'line', data: Array(history.timeline.length).fill(history.safe_target), itemStyle: { color: '#f59e0b' }, lineStyle: { type: 'dashed' } },
      { name: 'Contract Demand', type: 'line', data: Array(history.timeline.length).fill(history.contract_demand), itemStyle: { color: '#ef4444' } }
    ]
  };

  const assetOption = {
    title: { text: 'Asset Contribution', textStyle: { fontSize: 12, fontWeight: 'bold', color: '#64748b' } },
    tooltip: { trigger: 'axis', axisPointer: { type: 'line', label: { backgroundColor: '#6a7985' } } },
    legend: { data: ['Production', 'Utility', 'HVAC', 'Auxiliary'], bottom: 0, textStyle: {fontSize: 10} },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '15%', containLabel: true },
    xAxis: [{ type: 'category', boundaryGap: false, data: history.timeline }],
    yAxis: [{ type: 'value', name: 'kW' }],
    series: [
      { name: 'Auxiliary', type: 'line', stack: 'Total', areaStyle: {}, data: history.categories.Auxiliary },
      { name: 'HVAC', type: 'line', stack: 'Total', areaStyle: {}, data: history.categories.HVAC },
      { name: 'Utility', type: 'line', stack: 'Total', areaStyle: {}, data: history.categories.Utility },
      { name: 'Production', type: 'line', stack: 'Total', areaStyle: {}, data: history.categories.Production }
    ]
  };

  // Fake heatmap data for industrial look
  const hours = Array.from({length: 24}, (_, i) => `${i}:00`);
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const heatmapData = [];
  for (let i = 0; i < 7; i++) {
    for (let j = 0; j < 24; j++) {
       // Higher between 8 and 18
       let val = 40 + Math.random() * 20;
       if (j >= 8 && j <= 18) val += 30 + Math.random() * 10;
       heatmapData.push([j, i, val.toFixed(1)]);
    }
  }

  const heatmapOption = {
    title: { text: 'Energy Heatmap (kW)', textStyle: { fontSize: 12, fontWeight: 'bold', color: '#64748b' } },
    tooltip: { position: 'top' },
    grid: { left: '3%', right: '4%', bottom: '5%', top: '15%', containLabel: true },
    xAxis: { type: 'category', data: hours, splitArea: { show: true } },
    yAxis: { type: 'category', data: days, splitArea: { show: true } },
    visualMap: { min: 30, max: 110, calculable: true, orient: 'horizontal', left: 'center', bottom: '0%', show: false, inRange: { color: ['#f8fafc', '#bae6fd', '#3b82f6', '#1d4ed8'] } },
    series: [{ name: 'Demand', type: 'heatmap', data: heatmapData, label: { show: false }, emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } } }]
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto font-mono">
       <div className="bg-white text-slate-800 p-4 rounded-xl border-2 border-slate-200 shadow flex justify-between items-center">
          <div>
             <h1 className="text-xl lg:text-2xl font-bold font-bold uppercase tracking-widest text-teal-500">Energy Intelligence</h1>
             <p className="text-lg font-bold text-slate-800 mt-1">Historical analytics, shift comparison, and intensity metrics.</p>
          </div>
       </div>

       {/* SHIFT ANALYTICS */}
       <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-xl shadow-sm border-2 border-slate-200">
             <div className="flex justify-between items-center mb-4 border-b border-slate-100 pb-2">
                <h3 className="font-bold text-slate-700 uppercase tracking-wider text-base font-bold">Morning Shift (06:00-14:00)</h3>
                <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-base font-bold font-bold">BEST SHIFT</span>
             </div>
             <div className="space-y-2 text-lg font-bold">
                <div className="flex justify-between"><span className="text-slate-800">Energy Intensity</span><span className="font-bold">3.4 kWh / ton</span></div>
                <div className="flex justify-between"><span className="text-slate-800">Peak Events</span><span className="font-bold text-red-500">2</span></div>
                <div className="flex justify-between"><span className="text-slate-800">Idle Waste</span><span className="font-bold">4.2%</span></div>
             </div>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border-2 border-slate-200">
             <div className="flex justify-between items-center mb-4 border-b border-slate-100 pb-2">
                <h3 className="font-bold text-slate-700 uppercase tracking-wider text-base font-bold">Evening Shift (14:00-22:00)</h3>
                <span className="px-2 py-0.5 bg-orange-100 text-orange-700 rounded text-base font-bold font-bold">HIGH INTENSITY</span>
             </div>
             <div className="space-y-2 text-lg font-bold">
                <div className="flex justify-between"><span className="text-slate-800">Energy Intensity</span><span className="font-bold text-orange-600">4.1 kWh / ton</span></div>
                <div className="flex justify-between"><span className="text-slate-800">Peak Events</span><span className="font-bold text-red-500">5</span></div>
                <div className="flex justify-between"><span className="text-slate-800">Idle Waste</span><span className="font-bold">6.8%</span></div>
             </div>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border-2 border-slate-200">
             <div className="flex justify-between items-center mb-4 border-b border-slate-100 pb-2">
                <h3 className="font-bold text-slate-700 uppercase tracking-wider text-base font-bold">Night Shift (22:00-06:00)</h3>
                <span className="px-2 py-0.5 bg-slate-50 text-slate-800 rounded text-base font-bold font-bold">BASELINE</span>
             </div>
             <div className="space-y-2 text-lg font-bold">
                <div className="flex justify-between"><span className="text-slate-800">Energy Intensity</span><span className="font-bold">3.8 kWh / ton</span></div>
                <div className="flex justify-between"><span className="text-slate-800">Peak Events</span><span className="font-bold text-green-500">0</span></div>
                <div className="flex justify-between"><span className="text-slate-800">Idle Waste</span><span className="font-bold text-red-500">12.4%</span></div>
             </div>
          </div>
       </div>

      <div className="grid grid-cols-1 gap-4">
        <div className="bg-white p-4 rounded-xl border-2 border-slate-200 shadow-sm">
          <ReactECharts option={demandOption} style={{ height: '300px', width: '100%' }} opts={{ renderer: 'svg' }} />
        </div>
        
        <div className="bg-white p-4 rounded-xl border-2 border-slate-200 shadow-sm">
          <ReactECharts option={heatmapOption} style={{ height: '300px', width: '100%' }} opts={{ renderer: 'svg' }} />
        </div>

        <div className="bg-white p-4 rounded-xl border-2 border-slate-200 shadow-sm">
          <ReactECharts option={assetOption} style={{ height: '300px', width: '100%' }} opts={{ renderer: 'svg' }} />
        </div>
      </div>
    </div>
  )
}
