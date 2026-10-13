"use client"
import { ClientModeBoundary } from "@/components/ClientModeBoundary"

import React, { useEffect, useState } from 'react'

export default function BusinessImpactPage() {
  const [impact, setImpact] = useState<any>(null)

  useEffect(() => {
    const fetchImpact = async () => {
      const res = await fetch(`${(typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))}/business-impact`)
      const data = await res.json()
      setImpact(data)
    }
    fetchImpact()
  }, [])

  if (!impact) return <div className="text-slate-800 p-10">Loading Business Impact Data...</div>

  // Carbon Intelligence Assumptions
  const CARBON_FACTOR = 0.71; // kgCO2e/kWh (Grid average)

  return (
    
    <div className="max-w-[1400px] mx-auto space-y-6">
      <div className="bg-white p-4 rounded-xl border-2 border-neutral-200 shadow-sm flex justify-between items-center">
        <div>
          <h1 className="text-xl lg:text-2xl font-bold font-bold text-slate-800 tracking-tight">Business & Carbon Impact</h1>
          <p className="text-lg font-bold text-slate-800 mt-1">Economic Modelling and Carbon Emission Intelligence</p>
        </div>
        <div className="text-right">
          <div className="text-base font-bold uppercase font-bold text-slate-800">Tariff Configuration</div>
          <div className="font-mono text-lg font-bold font-semibold text-slate-700">₹7.5/kWh + ₹350/kW (Demand)</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Measured */}
        <div className="bg-white p-4 rounded-xl border-2 border-neutral-200 shadow-sm relative overflow-hidden md:col-span-1">
          <div className="absolute top-0 left-0 w-full h-1 bg-slate-400"></div>
          <div className="flex justify-between items-start mb-6">
            <h3 className="font-bold text-slate-800">Operational Baseline</h3>
            <span className="px-2 py-0.5 rounded text-base font-bold font-bold bg-slate-50 text-slate-800 uppercase border-2 border-slate-200">MEASURED</span>
          </div>
          <div className="space-y-6">
            <div>
              <div className="text-base font-bold font-bold text-slate-800 uppercase tracking-wider">Energy Consumed (Today)</div>
              <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">{impact.today.energy_kwh.toLocaleString()} <span className="text-lg font-bold text-slate-800 font-medium">kWh</span></div>
            </div>
            <div>
              <div className="text-base font-bold font-bold text-slate-800 uppercase tracking-wider">Peak Demand (Today)</div>
              <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">{impact.today.peak_demand_kw} <span className="text-lg font-bold text-slate-800 font-medium">kW</span></div>
            </div>
            <div className="pt-4 border-t border-slate-100">
              <div className="text-base font-bold font-bold text-slate-800 uppercase tracking-wider">Cost of Energy (Today)</div>
              <div className="text-xl lg:text-2xl font-bold font-medium text-slate-700">₹{impact.today.energy_cost_inr.toLocaleString()}</div>
            </div>
          </div>
        </div>

        {/* Simulated */}
        <div className="bg-white p-4 rounded-xl border-2 border-teal-200 shadow-sm bg-teal-50/30 relative overflow-hidden md:col-span-1">
          <div className="absolute top-0 left-0 w-full h-1 bg-blue-400"></div>
          <div className="flex justify-between items-start mb-6">
            <h3 className="font-bold text-slate-800">AI Optimization</h3>
            <span className="px-2 py-0.5 rounded text-base font-bold font-bold bg-blue-100 text-blue-700 uppercase border-2 border-teal-200">SIMULATED</span>
          </div>
          <div className="space-y-6">
            <div>
              <div className="text-base font-bold font-bold text-teal-700 uppercase tracking-wider">Avoided Demand Penalty</div>
              <div className="text-xl lg:text-2xl font-bold font-bold text-blue-800">{impact.simulation.potential_peak_reduction_kw} <span className="text-lg font-bold text-teal-700 font-medium">kW</span></div>
            </div>
            <div>
              <div className="text-base font-bold font-bold text-teal-700 uppercase tracking-wider">Daily Energy Reduction</div>
              <div className="text-xl lg:text-2xl font-bold font-bold text-blue-800">{impact.simulation.potential_reduction_kwh} <span className="text-lg font-bold text-teal-700 font-medium">kWh</span></div>
            </div>
            <div className="pt-4 border-t border-blue-100">
              <div className="text-base font-bold font-bold text-teal-700 uppercase tracking-wider">Production Impact</div>
              <div className="text-xl lg:text-2xl font-bold font-bold text-green-600">0.0%</div>
            </div>
          </div>
        </div>

        {/* Carbon Intelligence */}
        <div className="bg-white p-4 rounded-xl border-2 border-emerald-200 shadow-sm bg-emerald-50/30 relative overflow-hidden md:col-span-1">
          <div className="absolute top-0 left-0 w-full h-1 bg-emerald-500"></div>
          <div className="flex justify-between items-start mb-6">
            <h3 className="font-bold text-slate-800">Carbon Intelligence</h3>
            <span className="px-2 py-0.5 rounded text-base font-bold font-bold bg-emerald-100 text-emerald-700 uppercase border-2 border-emerald-200">CALCULATED</span>
          </div>
          <div className="space-y-6">
            <div>
              <div className="text-base font-bold font-bold text-emerald-700 uppercase tracking-wider">Gross Carbon Impact</div>
              <div className="text-xl lg:text-2xl font-bold font-bold text-emerald-600">{(impact.today.energy_kwh * CARBON_FACTOR).toLocaleString(undefined, {maximumFractionDigits: 1})} <span className="text-lg font-bold text-emerald-600 font-medium">kgCO₂e</span></div>
            </div>
            <div>
              <div className="text-base font-bold font-bold text-emerald-700 uppercase tracking-wider">Potential AI Reduction</div>
              <div className="text-xl lg:text-2xl font-bold font-bold text-emerald-800">-{(impact.simulation.potential_reduction_kwh * CARBON_FACTOR).toLocaleString(undefined, {maximumFractionDigits: 1})} <span className="text-lg font-bold text-emerald-600 font-medium">kgCO₂e/day</span></div>
            </div>
            <div className="pt-4 border-t border-emerald-100">
              <div className="text-base font-bold font-bold text-emerald-700 uppercase tracking-wider">Emission Factor (Scope 2)</div>
              <div className="text-lg font-bold font-medium text-emerald-800">{CARBON_FACTOR} kgCO₂e/kWh</div>
            </div>
          </div>
        </div>

        {/* Projected */}
        <div className="bg-white p-4 rounded-xl border-2 border-amber-200 shadow-sm bg-amber-50/30 relative overflow-hidden md:col-span-1">
          <div className="absolute top-0 left-0 w-full h-1 bg-amber-500"></div>
          <div className="flex justify-between items-start mb-6">
            <h3 className="font-bold text-slate-800">Financial Impact</h3>
            <span className="px-2 py-0.5 rounded text-base font-bold font-bold bg-amber-100 text-amber-700 uppercase border-2 border-amber-200">PROJECTED</span>
          </div>
          <div className="space-y-6">
            <div>
              <div className="text-base font-bold font-bold text-amber-700 uppercase tracking-wider">Annualized Opportunity</div>
              <div className="text-xl lg:text-xl lg:text-2xl font-bold font-bold text-amber-600">₹{impact.projection.annual_opportunity_inr.toLocaleString()}</div>
            </div>
            <div className="pt-4 border-t border-amber-100">
              <div className="text-base font-bold font-bold text-amber-700 uppercase tracking-wider">Estimated Payback Period</div>
              <div className="text-xl lg:text-2xl font-bold font-medium text-amber-800">{impact.projection.roi_months} Months</div>
            </div>
          </div>
        </div>

      </div>

      <div className="bg-white p-4 rounded-xl border-2 border-neutral-200 shadow-sm">
         <h3 className="font-semibold text-slate-800 uppercase tracking-wider text-base font-bold mb-4">Tariff Optimization Model</h3>
         <div className="h-64 flex flex-col justify-center border-t border-slate-100 pt-6">
            <div className="flex justify-between items-center text-lg font-bold border-b border-slate-50 pb-3">
               <span className="text-slate-800">Base Energy Cost (Projected Annual)</span>
               <span className="font-mono font-medium">₹{(impact.today.energy_cost_inr * 365).toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center text-lg font-bold border-b border-slate-50 py-3">
               <span className="text-slate-800">Peak Demand Penalty (Avoidable)</span>
               <span className="font-mono font-medium text-red-500">+ ₹{(impact.simulation.potential_peak_reduction_kw * 350 * 12).toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center text-lg font-bold py-3 font-bold">
               <span className="text-slate-800">Total Unoptimized Projected Cost</span>
               <span className="font-mono text-slate-800">₹{((impact.today.energy_cost_inr * 365) + (impact.simulation.potential_peak_reduction_kw * 350 * 12)).toLocaleString()}</span>
            </div>
         </div>
      </div>
    </div>
    
  )
}
