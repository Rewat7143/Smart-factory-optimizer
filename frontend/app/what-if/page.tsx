"use client"
import React, { useState } from 'react'

export default function WhatIfPage() {
  const [params, setParams] = useState({
    compressor_delay_min: 0,
    pump_delay_min: 0,
    hvac_level_percent: 100,
    production_target: 100,
    battery_available: false,
    demand_target: 90.0
  })

  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleSimulate = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${(typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))}/what-if`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      })
      const data = await res.json()
      setResult(data)
    } finally {
      setLoading(false)
    }
  }

  const handleParamChange = (e: any) => {
    const { name, value, type, checked } = e.target
    setParams({
      ...params,
      [name]: type === 'checkbox' ? checked : Number(value)
    })
  }

  return (
    <div>
      <div className="flex justify-between items-end mb-6">
        <div>
          <h2 className="text-lg font-semibold text-slate-800">Counterfactual What-If Simulator</h2>
          <p className="text-lg font-bold text-slate-800 mt-1">Simulate interactive operational scenarios to evaluate peak, cost, and risk impacts.</p>
        </div>
        <span className="px-2.5 py-0.5 rounded text-base font-bold font-bold bg-amber-100 text-amber-800 border-2 border-amber-200">
          SIMULATION
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        
        {/* Controls */}
        <div className="lg:col-span-1 bg-white p-5 rounded-xl border-2 border-neutral-200 shadow-sm space-y-6">
          <h3 className="font-semibold text-lg font-bold text-slate-700 border-b border-slate-100 pb-2">Control Variables</h3>
          
          <div>
            <label className="block text-base font-bold font-medium text-slate-800 mb-1">Compressor Delay (min)</label>
            <input type="range" name="compressor_delay_min" min="0" max="30" value={params.compressor_delay_min} onChange={handleParamChange} className="w-full" />
            <div className="text-right text-base font-bold font-bold text-slate-800">{params.compressor_delay_min} min</div>
          </div>
          
          <div>
            <label className="block text-base font-bold font-medium text-slate-800 mb-1">Pump Delay (min)</label>
            <input type="range" name="pump_delay_min" min="0" max="30" value={params.pump_delay_min} onChange={handleParamChange} className="w-full" />
            <div className="text-right text-base font-bold font-bold text-slate-800">{params.pump_delay_min} min</div>
          </div>

          <div>
            <label className="block text-base font-bold font-medium text-slate-800 mb-1">HVAC Setpoint Duty (%)</label>
            <input type="range" name="hvac_level_percent" min="50" max="100" step="5" value={params.hvac_level_percent} onChange={handleParamChange} className="w-full" />
            <div className="text-right text-base font-bold font-bold text-slate-800">{params.hvac_level_percent}%</div>
          </div>

          <div>
            <label className="block text-base font-bold font-medium text-slate-800 mb-1">Production Target (%)</label>
            <input type="number" name="production_target" min="50" max="100" value={params.production_target} onChange={handleParamChange} className="w-full border-2 border-slate-300 rounded p-1 text-lg font-bold" />
          </div>

          <div className="flex items-center space-x-2">
            <input type="checkbox" name="battery_available" id="batt" checked={params.battery_available} onChange={handleParamChange} className="rounded border-slate-300" />
            <label htmlFor="batt" className="text-lg font-bold font-medium text-slate-700">Battery Available</label>
          </div>

          <button onClick={handleSimulate} disabled={loading} className="w-full bg-teal-700 text-white hover:bg-blue-700 text-slate-800 font-medium py-2 rounded transition-colors text-lg font-bold">
            {loading ? 'Simulating...' : 'Run Simulation'}
          </button>
        </div>

        {/* Results */}
        <div className="lg:col-span-3">
          {!result ? (
            <div className="bg-white h-full border-2 border-neutral-200 rounded-xl p-10 flex flex-col items-center justify-center text-slate-800 shadow-sm">
              Adjust parameters and run the simulation to see counterfactual outcomes.
            </div>
          ) : (
            <div className="bg-white border-2 border-neutral-200 rounded-xl shadow-sm overflow-hidden">
              <table className="min-w-full divide-y divide-neutral-200 text-lg font-bold">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800 uppercase text-base font-bold">Metric</th>
                    <th className="px-6 py-4 text-center font-semibold text-slate-800 uppercase text-base font-bold border-l border-slate-200">Baseline (Do Nothing)</th>
                    <th className="px-6 py-4 text-center font-bold text-green-700 uppercase text-base font-bold border-l border-green-200 bg-green-50">Optimized Schedule</th>
                    <th className="px-6 py-4 text-center font-semibold text-slate-800 uppercase text-base font-bold border-l border-slate-200">Option A (Compressor Only)</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-neutral-100">
                  <tr className="hover:bg-slate-50">
                    <td className="px-6 py-4 font-medium text-slate-800">Peak Demand</td>
                    <td className="px-6 py-4 text-center text-slate-800 border-l border-slate-200 font-bold">{result.baseline.peak_kw} kW</td>
                    <td className="px-6 py-4 text-center text-green-700 border-l border-green-200 bg-green-50/50 font-bold">{result.optimized.peak_kw} kW</td>
                    <td className="px-6 py-4 text-center text-slate-800 border-l border-slate-200 font-bold">{result.option_a.peak_kw} kW</td>
                  </tr>
                  <tr className="hover:bg-slate-50">
                    <td className="px-6 py-4 font-medium text-slate-800">Energy Consumption</td>
                    <td className="px-6 py-4 text-center text-slate-800 border-l border-slate-200">{result.baseline.energy_kwh} kWh</td>
                    <td className="px-6 py-4 text-center text-green-700 border-l border-green-200 bg-green-50/50">{result.optimized.energy_kwh} kWh</td>
                    <td className="px-6 py-4 text-center text-slate-800 border-l border-slate-200">{result.option_a.energy_kwh} kWh</td>
                  </tr>
                  <tr className="hover:bg-slate-50">
                    <td className="px-6 py-4 font-medium text-slate-800">Estimated Cost</td>
                    <td className="px-6 py-4 text-center text-slate-800 border-l border-slate-200">₹{result.baseline.cost_inr.toLocaleString()}</td>
                    <td className="px-6 py-4 text-center text-green-700 border-l border-green-200 bg-green-50/50 font-medium">₹{result.optimized.cost_inr.toLocaleString()}</td>
                    <td className="px-6 py-4 text-center text-slate-800 border-l border-slate-200">₹{result.option_a.cost_inr.toLocaleString()}</td>
                  </tr>
                  <tr className="hover:bg-slate-50">
                    <td className="px-6 py-4 font-medium text-slate-800">Production Impact</td>
                    <td className="px-6 py-4 text-center text-slate-800 border-l border-slate-200 font-bold">{result.baseline.production_percent}%</td>
                    <td className="px-6 py-4 text-center text-green-700 border-l border-green-200 bg-green-50/50 font-bold">{result.optimized.production_percent}%</td>
                    <td className="px-6 py-4 text-center text-slate-800 border-l border-slate-200 font-bold">{result.option_a.production_percent}%</td>
                  </tr>
                  <tr className="hover:bg-slate-50">
                    <td className="px-6 py-4 font-medium text-slate-800">Peak Risk Level</td>
                    <td className="px-6 py-4 text-center border-l border-slate-200">
                      <span className={`px-2 py-1 rounded text-base font-bold font-bold ${result.baseline.peak_risk === 'HIGH' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>{result.baseline.peak_risk}</span>
                    </td>
                    <td className="px-6 py-4 text-center border-l border-green-200 bg-green-50/50">
                      <span className={`px-2 py-1 rounded text-base font-bold font-bold ${result.optimized.peak_risk === 'HIGH' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>{result.optimized.peak_risk}</span>
                    </td>
                    <td className="px-6 py-4 text-center border-l border-slate-200">
                      <span className={`px-2 py-1 rounded text-base font-bold font-bold ${result.option_a.peak_risk === 'HIGH' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>{result.option_a.peak_risk}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
