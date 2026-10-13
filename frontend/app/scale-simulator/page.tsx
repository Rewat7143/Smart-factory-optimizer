"use client"
import React, { useState } from 'react'
import ReactECharts from 'echarts-for-react'
import { useGlobalState } from '@/components/GlobalState'

export default function ScaleSimulatorPage() {
  const { mode } = useGlobalState()
  
  // User Controls
  const [factories, setFactories] = useState<number>(100)
  const [assetsPerFactory, setAssetsPerFactory] = useState<number>(20)
  const [hoursPerDay, setHoursPerDay] = useState<number>(16)
  const [daysPerMonth, setDaysPerMonth] = useState<number>(24)
  const [baselineKw, setBaselineKw] = useState<number>(45) // per asset avg
  const [tariff, setTariff] = useState<number>(7.5)
  const [deploymentCostPerFactory, setDeploymentCostPerFactory] = useState<number>(150000) // ₹1.5L
  const [scenario, setScenario] = useState<'CONSERVATIVE' | 'BASE' | 'OPTIMISTIC'>('BASE')

  // Savings Assumptions
  const savingsRates = {
    CONSERVATIVE: 0.04, // 4%
    BASE: 0.08,         // 8%
    OPTIMISTIC: 0.14    // 14%
  }
  
  const rate = savingsRates[scenario]

  // Calculations
  const baselineKwhPerDayPerFactory = assetsPerFactory * baselineKw * hoursPerDay
  const baselineKwhPerMonthPerFactory = baselineKwhPerDayPerFactory * daysPerMonth
  const baselineKwhAnnualFleet = baselineKwhPerMonthPerFactory * 12 * factories

  const savedKwhAnnualFleet = baselineKwhAnnualFleet * rate
  const savedCostAnnualFleet = savedKwhAnnualFleet * tariff
  
  const deploymentCostFleet = factories * deploymentCostPerFactory
  const paybackYears = deploymentCostFleet / savedCostAnnualFleet
  const roi = ((savedCostAnnualFleet - deploymentCostFleet) / deploymentCostFleet) * 100

  // Fleet Growth Chart Data
  const fleetSizes = [1, 10, 50, 100, 500, 1000]
  const growthData = fleetSizes.map(size => {
    return (baselineKwhPerMonthPerFactory * 12 * size * rate * tariff) / 10000000 // In Crores
  })

  // Scenario Comparison Data
  const scenarioData = [
    (baselineKwhAnnualFleet * savingsRates.CONSERVATIVE * tariff) / 10000000,
    (baselineKwhAnnualFleet * savingsRates.BASE * tariff) / 10000000,
    (baselineKwhAnnualFleet * savingsRates.OPTIMISTIC * tariff) / 10000000
  ]

  const formatCurrency = (val: number) => {
    if (val > 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`
    if (val > 100000) return `₹${(val / 100000).toFixed(2)} L`
    return `₹${Math.round(val).toLocaleString()}`
  }

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 font-mono text-slate-800 pb-20 p-4">
      
      {/* HEADER */}
      <div className="flex justify-between items-end border-b border-slate-300 pb-4">
        <div>
          <h1 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-800 uppercase">Scale Impact Simulator</h1>
          <p className="text-sm font-semibold tracking-widest text-slate-500 uppercase mt-2">Projected Industrial Fleet Optimization</p>
        </div>
        <div className="flex items-center gap-2 text-indigo-700 font-bold tracking-widest text-xs uppercase px-3 py-1 bg-indigo-50 border border-indigo-200 rounded">
          Interactive Scenario Mode
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* CONTROLS */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white border border-slate-300 rounded-xl p-5 shadow-sm space-y-5">
            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-800 border-b border-slate-200 pb-2">Fleet Parameters</h3>
            
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wider">Number of Factories ({factories})</label>
              <input type="range" min="1" max="1000" step="1" value={factories} onChange={e => setFactories(Number(e.target.value))} className="w-full accent-indigo-600" />
            </div>
            
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wider">Assets per Factory ({assetsPerFactory})</label>
              <input type="range" min="5" max="100" step="1" value={assetsPerFactory} onChange={e => setAssetsPerFactory(Number(e.target.value))} className="w-full accent-indigo-600" />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wider">Baseline Asset Load ({baselineKw} kW)</label>
              <input type="range" min="10" max="250" step="5" value={baselineKw} onChange={e => setBaselineKw(Number(e.target.value))} className="w-full accent-indigo-600" />
            </div>

            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-800 border-b border-slate-200 pb-2 pt-2">Operational Hours</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase">Hrs / Day</label>
                <input type="number" value={hoursPerDay} onChange={e => setHoursPerDay(Number(e.target.value))} className="w-full bg-slate-50 border border-slate-300 rounded p-1 text-sm font-bold" />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase">Days / Mo</label>
                <input type="number" value={daysPerMonth} onChange={e => setDaysPerMonth(Number(e.target.value))} className="w-full bg-slate-50 border border-slate-300 rounded p-1 text-sm font-bold" />
              </div>
            </div>

            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-800 border-b border-slate-200 pb-2 pt-2">Financial Assumptions</h3>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wider">Tariff Rate (₹/kWh)</label>
              <input type="number" step="0.5" value={tariff} onChange={e => setTariff(Number(e.target.value))} className="w-full bg-slate-50 border border-slate-300 rounded p-1 text-sm font-bold" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wider">Deployment Cost / Factory (₹)</label>
              <input type="number" step="10000" value={deploymentCostPerFactory} onChange={e => setDeploymentCostPerFactory(Number(e.target.value))} className="w-full bg-slate-50 border border-slate-300 rounded p-1 text-sm font-bold" />
            </div>

            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-800 border-b border-slate-200 pb-2 pt-2">Optimization Scenario</h3>
            <div className="flex gap-2">
              {['CONSERVATIVE', 'BASE', 'OPTIMISTIC'].map(s => (
                <button key={s} onClick={() => setScenario(s as any)} className={`flex-1 text-[10px] py-1.5 rounded border font-bold tracking-widest uppercase transition-colors ${scenario === s ? 'bg-indigo-600 text-white border-indigo-700' : 'bg-slate-100 text-slate-500 border-slate-200 hover:bg-slate-200'}`}>
                  {s}
                </button>
              ))}
            </div>
            <div className="text-[10px] text-slate-500 leading-tight">
              Assumes {rate * 100}% energy reduction in this scenario.
            </div>

          </div>
        </div>

        {/* OUTPUTS */}
        <div className="lg:col-span-3 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
             <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-sm text-center text-white">
                <div className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">Annual Savings</div>
                <div className="text-3xl font-bold">{formatCurrency(savedCostAnnualFleet)}</div>
             </div>
             <div className="bg-white border border-slate-300 rounded-xl p-5 shadow-sm text-center">
                <div className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2">Energy Avoided</div>
                <div className="text-3xl font-bold text-slate-800">{(savedKwhAnnualFleet / 1000000).toFixed(2)} MWh</div>
             </div>
             <div className="bg-white border border-slate-300 rounded-xl p-5 shadow-sm text-center">
                <div className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2">Payback Period</div>
                <div className="text-3xl font-bold text-slate-800">{paybackYears.toFixed(1)} Yrs</div>
             </div>
             <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-5 shadow-sm text-center">
                <div className="text-xs font-semibold uppercase tracking-widest text-indigo-500 mb-2">Est. ROI (1 Yr)</div>
                <div className="text-3xl font-bold text-indigo-700">{roi > 0 ? '+' : ''}{roi.toFixed(0)}%</div>
             </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white border border-slate-300 rounded-xl p-6 shadow-sm">
               <div className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-2 border-b border-slate-200 pb-2">Fleet Scaling Trajectory</div>
               <ReactECharts
                  style={{ height: '300px' }}
                  option={{
                     tooltip: { trigger: 'axis', formatter: '{b} Factories: ₹{c} Cr/yr' },
                     xAxis: { type: 'category', data: fleetSizes, name: 'Factories', axisLabel: { color: '#64748b' } },
                     yAxis: { type: 'value', name: 'Annual Savings (₹ Cr)', axisLabel: { color: '#64748b' } },
                     series: [{
                        data: growthData, type: 'bar', itemStyle: { color: '#4f46e5', borderRadius: [4, 4, 0, 0] }
                     }],
                     grid: { left: '12%', right: '5%', top: '15%', bottom: '10%' }
                  }}
               />
            </div>

            <div className="bg-white border border-slate-300 rounded-xl p-6 shadow-sm">
               <div className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-2 border-b border-slate-200 pb-2">Scenario Impact Comparison</div>
               <ReactECharts
                  style={{ height: '300px' }}
                  option={{
                     tooltip: { trigger: 'axis', formatter: '{b} Scenario: ₹{c} Cr/yr' },
                     xAxis: { type: 'category', data: ['Conservative', 'Base', 'Optimistic'], axisLabel: { color: '#64748b' } },
                     yAxis: { type: 'value', name: 'Annual Savings (₹ Cr)', axisLabel: { color: '#64748b' } },
                     series: [{
                        data: scenarioData.map((val, idx) => ({
                           value: val,
                           itemStyle: { color: idx === 0 ? '#94a3b8' : idx === 1 ? '#4f46e5' : '#059669' }
                        })), 
                        type: 'bar', barWidth: '40%', itemStyle: { borderRadius: [4, 4, 0, 0] }
                     }],
                     grid: { left: '12%', right: '5%', top: '15%', bottom: '10%' }
                  }}
               />
            </div>
          </div>
          
          <div className="bg-amber-50 border border-amber-200 rounded p-4 text-xs font-semibold text-amber-800">
            <strong>Disclaimer:</strong> Outputs are strictly PROJECTED SCENARIOS based on user-supplied assumptions. These values do not represent verified savings.
          </div>
        </div>
      </div>
    </div>
  )
}
