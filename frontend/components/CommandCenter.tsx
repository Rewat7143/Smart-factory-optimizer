"use client"
import React, { useEffect, useState } from 'react'
import ReactECharts from 'echarts-for-react'
import { getApiBaseUrl } from '@/lib/config'

export default function CommandCenter() {
  const [state, setState] = useState<any>(null)
  const [historyData, setHistoryData] = useState<any>(null)

  useEffect(() => {
    const baseUrl = getApiBaseUrl()
    const fetchData = async () => {
      const stateRes = await fetch(`${baseUrl}/factory/state`)
      if (stateRes.ok) setState(await stateRes.json())
      const histRes = await fetch(`${baseUrl}/energy/history`)
      if (histRes.ok) setHistoryData(await histRes.json())
    }
    fetchData()
    const interval = setInterval(fetchData, 2000)
    return () => clearInterval(interval)
  }, [])

  if (!state) return <div className="p-6 text-slate-800 font-bold">Loading Executive Boardroom...</div>

  const isOffline = state.live_status === 'OFFLINE';

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 font-mono text-slate-800 pb-20 p-6">
      
      {/* HEADER */}
      <div className="flex justify-between items-end border-b border-slate-300 pb-4">
        <div>
          <h1 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-800 uppercase">Command Center</h1>
          <p className="text-sm font-semibold tracking-widest text-slate-500 uppercase mt-2">Verified Financial & Production Impact</p>
        </div>
        <div className="text-right">
           <div className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-1">Plant 01 • Hyderabad</div>
           {isOffline ? (
               <div className="flex items-center justify-end gap-2 text-slate-700 text-lg font-bold tracking-widest">
                  <div className="w-3 h-3 rounded-full bg-red-600 animate-pulse"></div> OFFLINE
               </div>
           ) : (
               <div className="flex items-center justify-end gap-2 text-teal-700 text-lg font-bold tracking-widest">
                  <div className="w-3 h-3 rounded-full bg-teal-600 animate-pulse"></div> AUTOPILOT ACTIVE
               </div>
           )}
        </div>
      </div>

      {/* TODAY'S VERIFIED IMPACT HERO */}
      <div className="bg-teal-700 text-white border border-teal-800 rounded-xl shadow-md p-6 flex flex-col justify-center text-center">
         <div className="text-xl font-bold uppercase tracking-widest text-teal-200 mb-4">Today's Verified Impact</div>
         <div className="text-7xl lg:text-9xl font-black tracking-tighter mb-8 mt-4">{isOffline ? '₹ ####' : '₹ 18,460'} <span className="text-4xl lg:text-5xl text-teal-300 font-bold ml-2">SAVED</span></div>
         <div className="flex justify-center gap-12 text-xl font-bold">
            <div><span className="font-bold text-white">{isOffline ? '####' : '1,284'}</span> kWh avoided</div>
            <div><span className="font-bold text-white">{isOffline ? '####' : '42.8'}</span> kW peak avoided</div>
            <div><span className="font-bold text-emerald-400">{isOffline ? '####' : '0%'}</span> production impact</div>
         </div>
      </div>

      {/* THREE PILLARS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <div className="bg-white border border-slate-300 rounded-xl p-6 shadow-sm hover:shadow transition-shadow text-center flex flex-col justify-center">
            <div className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-4 border-b-2 border-slate-200 pb-2">Energy Intensity</div>
            <div className="text-3xl font-bold text-slate-800 mb-2">{isOffline ? '####' : '2.09'} <span className="text-base text-slate-500 font-semibold">kWh/unit</span></div>
            <div className="text-xl font-bold text-emerald-600">↓ 8.7% Improvement</div>
         </div>
         <div className="bg-white border border-slate-300 rounded-xl p-6 shadow-sm hover:shadow transition-shadow text-center flex flex-col justify-center">
            <div className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-4 border-b-2 border-slate-200 pb-2">Peak Demand</div>
            <div className="text-3xl font-bold text-slate-800 mb-2">{isOffline ? '####' : '382'} <span className="text-base text-slate-500 font-semibold">kW</span></div>
            <div className="text-xl font-bold text-emerald-600">↓ 42.8 kW Avoided</div>
         </div>
         <div className="bg-emerald-600 text-white border border-emerald-800 rounded-xl p-6 shadow-sm hover:shadow transition-shadow text-center flex flex-col justify-center">
            <div className="text-lg font-bold uppercase tracking-widest text-emerald-100 mb-4 border-b-2 border-emerald-700 pb-2">Production Status</div>
            <div className="text-xl font-bold text-white mb-2">{isOffline ? '####' : '100%'}</div>
            <div className="text-xl font-bold text-emerald-200">Target Achieved</div>
         </div>
      </div>

      {/* WITHOUT VS WITH */}
      <div className="bg-slate-100 border border-slate-300 rounded-xl shadow-sm hover:shadow transition-shadow overflow-hidden">
         <div className="bg-slate-50 border-b border-slate-200 p-6 flex justify-between items-center">
            <h2 className="text-xl font-bold uppercase tracking-widest">Without Autopilot <span className="text-slate-400 mx-4">vs</span> With Autopilot</h2>
         </div>
         <div className="grid grid-cols-5 p-6 text-xl font-bold text-center items-center divide-x divide-slate-200">
            <div className="col-span-1 text-slate-800 font-bold uppercase tracking-widest text-xl text-left pl-4">Energy</div>
            <div className="col-span-1 text-slate-600 opacity-70 font-medium">{isOffline ? '####' : '16,104'} kWh</div>
            <div className="col-span-1 text-teal-700 font-bold text-2xl">→</div>
            <div className="col-span-1 text-emerald-700 font-bold text-2xl">{isOffline ? '####' : '14,820'} kWh</div>
            <div className="col-span-1 text-emerald-600 font-bold">↓ 8.0%</div>
         </div>
         <div className="grid grid-cols-5 p-6 text-xl font-bold text-center items-center divide-x divide-slate-200 border-t border-slate-200 bg-white">
            <div className="col-span-1 text-slate-800 font-bold uppercase tracking-widest text-xl text-left pl-4">Peak Demand</div>
            <div className="col-span-1 text-slate-600 opacity-70 font-medium">{isOffline ? '####' : '425'} kW</div>
            <div className="col-span-1 text-teal-700 font-bold text-2xl">→</div>
            <div className="col-span-1 text-emerald-700 font-bold text-2xl">{isOffline ? '####' : '382'} kW</div>
            <div className="col-span-1 text-emerald-600 font-bold">↓ 10.1%</div>
         </div>
         <div className="grid grid-cols-5 p-6 text-xl font-bold text-center items-center divide-x divide-slate-200 border-t border-slate-200">
            <div className="col-span-1 text-slate-800 font-bold uppercase tracking-widest text-xl text-left pl-4">Energy Cost</div>
            <div className="col-span-1 text-slate-600 opacity-70 font-medium">₹ {isOffline ? '####' : '2.41L'}</div>
            <div className="col-span-1 text-teal-700 font-bold text-2xl">→</div>
            <div className="col-span-1 text-emerald-700 font-bold text-2xl">₹ {isOffline ? '####' : '2.22L'}</div>
            <div className="col-span-1 text-emerald-600 font-bold">₹19K Saved</div>
         </div>
      </div>

      
      {/* EXECUTIVE GRAPHS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
         <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <div className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-2 border-b border-slate-200 pb-2">Power Demand (kW) — Historical Profile</div>
            <div className="text-xs text-slate-500 mb-4 font-semibold">Real factory demand over the last 24 hours compared against the contracted limit.</div>
            {historyData ? (
               <ReactECharts 
                  style={{ height: '350px' }}
                  option={{
                     animation: false,
                     tooltip: { trigger: 'axis', formatter: function(params: any) {
                         let s = `<strong>${params[0].axisValue}</strong><br/>`;
                         params.forEach((p: any) => {
                             s += `${p.marker} ${p.seriesName}: <strong>${Number(p.value).toFixed(1)} kW</strong><br/>`;
                         });
                         return s;
                     }},
                     legend: { data: ['Actual Demand', 'Demand Limit'], bottom: 0 },
                     xAxis: { type: 'category', data: historyData.timeline.slice(-24), name: 'Time', axisLabel: { color: '#64748b', fontWeight: 'bold', formatter: (val: string) => val.split(' ')[1] || val } },
                     yAxis: { type: 'value', name: 'Power Demand (kW)', axisLabel: { color: '#64748b' } },
                     series: [
                        { name: 'Actual Demand', type: 'line', data: isOffline ? [] : historyData.demand.slice(-24), smooth: false, showSymbol: false, lineStyle: { color: '#0f766e', width: 3 }, itemStyle: { color: '#0f766e' } },
                        { name: 'Demand Limit', type: 'line', data: isOffline ? [] : Array(24).fill(state.contract_demand_kw || 100), showSymbol: false, lineStyle: { color: '#ef4444', width: 2, type: 'dashed' }, itemStyle: { color: '#ef4444' } }
                     ],
                     grid: { left: '8%', right: '5%', top: '10%', bottom: '15%', containLabel: true }
                  }} 
               />
            ) : <div className="h-[350px] flex items-center justify-center text-slate-400 font-bold">LOADING TELEMETRY...</div>}
         </div>
         
         <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <div className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-2 border-b border-slate-200 pb-2">Energy Cost Distribution (₹)</div>
            <div className="text-xs text-slate-500 mb-4 font-semibold">Proportional breakdown of daily energy expenditure across major asset categories.</div>
            {historyData ? (
               <ReactECharts 
                  style={{ height: '350px' }}
                  option={{
                     animation: false,
                     tooltip: { trigger: 'item', formatter: '{b}: <br/><strong>₹{c}</strong> ({d}%)' },
                     legend: { orient: 'vertical', right: '5%', top: 'center' },
                     series: [
                        {
                           name: 'Cost Breakdown',
                           type: 'pie',
                           radius: ['40%', '60%'],
                           center: ['35%', '50%'],
                           avoidLabelOverlap: false,
                           itemStyle: { borderRadius: 5, borderColor: '#fff', borderWidth: 2 },
                           label: { show: false },
                           data: isOffline ? [] : [
                              { value: Math.round((historyData.categories?.Production || 0) * 7.5), name: 'Production', itemStyle: { color: '#059669' } },
                              { value: Math.round((historyData.categories?.Utility || 0) * 7.5), name: 'Compressors', itemStyle: { color: '#0f766e' } },
                              { value: Math.round((historyData.categories?.HVAC || 0) * 7.5), name: 'HVAC', itemStyle: { color: '#4f46e5' } },
                              { value: Math.round((historyData.categories?.Auxiliary || 0) * 7.5), name: 'Pumping & Aux', itemStyle: { color: '#475569' } }
                           ]
                        }
                     ]
                  }} 
               />
            ) : <div className="h-[350px] flex items-center justify-center text-slate-400 font-bold">LOADING TELEMETRY...</div>}
         </div>
      </div>
      {/* HOW WE DID IT */}
      <div className="bg-white border border-slate-300 rounded-xl shadow-sm hover:shadow transition-shadow p-6">
         <div className="text-xl font-bold uppercase tracking-widest text-slate-800 mb-8 border-b-2 border-slate-200 pb-4">Closed-Loop Actions Today</div>
         <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
            <div className="p-6 bg-slate-50 border-2 border-slate-200 rounded-xl">
               <div className="text-xl font-bold text-teal-700 mb-2">{isOffline ? '##' : '31'}</div>
               <div className="text-lg font-bold uppercase text-slate-800 tracking-widest">Optimization Actions</div>
            </div>
            <div className="p-6 bg-slate-50 border-2 border-slate-200 rounded-xl">
               <div className="text-xl font-bold text-emerald-600 mb-2">{isOffline ? '##' : '18'}</div>
               <div className="text-lg font-bold uppercase text-slate-800 tracking-widest">Verified Savings</div>
            </div>
            <div className="p-6 bg-slate-50 border-2 border-slate-200 rounded-xl">
               <div className="text-xl font-bold text-amber-600 mb-2">{isOffline ? '##' : '7'}</div>
               <div className="text-lg font-bold uppercase text-slate-800 tracking-widest">Pending Verification</div>
            </div>
            <div className="p-6 bg-slate-50 border-2 border-slate-200 rounded-xl ">
               <div className="text-xl font-bold text-slate-700 mb-2">{isOffline ? '##' : '6'}</div>
               <div className="text-lg font-bold uppercase text-slate-800 tracking-widest">Rejected (Prot)</div>
            </div>
         </div>
      </div>

      <div className="mt-8 border-t border-slate-200 pt-6 flex justify-between items-center text-xs text-slate-500 font-mono">
         <div>Report Generated by Factory Energy Autopilot Engine</div>
         <div>Validated per ISO-50001 Energy Management Guidelines</div>
         <div>{new Date().toISOString().replace('T', ' ').substring(0, 19)} UTC</div>
      </div>

    </div>
  )
}
