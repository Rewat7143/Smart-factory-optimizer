"use client"
import React, { useEffect, useState } from 'react'

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<any[]>([])

  useEffect(() => {
    const fetchOpps = async () => {
      const res = await fetch(`${(typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))}/opportunities`)
      const data = await res.json()
      setOpportunities(data)
    }
    fetchOpps()
    const interval = setInterval(fetchOpps, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      <div className="flex justify-between items-end mb-6">
        <div>
          <h2 className="text-lg font-semibold text-slate-800">Energy Opportunity Engine</h2>
          <p className="text-lg font-bold text-slate-800 mt-1">Live detected inefficiencies and actionable recommendations.</p>
        </div>
      </div>

      {opportunities.length === 0 ? (
        <div className="bg-white p-10 rounded-xl border-2 border-neutral-200 text-center text-slate-800 shadow-sm">
          No energy opportunities currently detected. The factory is running optimally.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {opportunities.map((opp) => (
            <div key={opp.opportunity_id} className="bg-white rounded-xl border-2 border-neutral-200 shadow-sm overflow-hidden flex flex-col md:flex-row">
              <div className={`w-2 md:w-3 ${opp.status === 'ACTION_REQUIRED' ? 'bg-amber-500' : 'bg-teal-500'}`}></div>
              <div className="p-4 flex-1 grid grid-cols-1 md:grid-cols-3 gap-4">
                
                <div className="md:col-span-1">
                  <div className="text-base font-bold font-bold text-slate-800 uppercase tracking-wider mb-1">{opp.opportunity_id}</div>
                  <h3 className="font-semibold text-slate-800 mb-2">{opp.category.replace('_', ' ')}</h3>
                  <div className="text-lg font-bold text-slate-800 space-y-1">
                    <p><span className="font-medium">Asset:</span> {opp.asset_name} ({opp.asset_id})</p>
                    <p><span className="font-medium">Confidence:</span> {opp.confidence}</p>
                    <p><span className="font-medium">Production Impact:</span> <span className="text-green-600 font-bold">{opp.production_impact}</span></p>
                  </div>
                </div>

                <div className="md:col-span-2 flex flex-col justify-between">
                  
                  <div>
                    <div className="text-base font-bold font-semibold text-slate-800 uppercase tracking-wider mb-2">Recommendation & Constraints</div>
                    <p className="text-slate-800 text-lg font-bold bg-slate-50 p-5 rounded border-2 border-slate-100 mb-2">{opp.recommended_action}</p>
                    <div className="flex gap-4 text-sm mt-3">
                        <div className="bg-slate-50 border border-slate-200 px-3 py-2 rounded">
                            <span className="font-bold text-slate-500 uppercase text-[10px] block mb-1">Expected Change</span>
                            <span className="font-bold text-slate-800">{opp.expected_kw_change || '-'}</span>
                        </div>
                        <div className="bg-slate-50 border border-slate-200 px-3 py-2 rounded">
                            <span className="font-bold text-slate-500 uppercase text-[10px] block mb-1">Financial Impact</span>
                            <span className="font-bold text-emerald-600">{opp.potential_monthly_inr || '-'}</span>
                        </div>
                        <div className="bg-slate-50 border border-slate-200 px-3 py-2 rounded flex-1">
                            <span className="font-bold text-slate-500 uppercase text-[10px] block mb-1">Production Constraint</span>
                            <span className="font-semibold text-slate-600">{opp.production_constraint || 'None'}</span>
                        </div>
                    </div>
                  </div>

                  
                  <div className="grid grid-cols-2 gap-4 mt-6">
                    <div className="bg-green-50 p-5 rounded-lg border-2 border-green-100">
                      <div className="text-base font-bold uppercase font-semibold text-green-700">Cost Opportunity</div>
                      <div className="text-xl lg:text-2xl font-bold font-bold text-green-700">₹{opp.cost_opportunity_inr.toLocaleString()}</div>
                    </div>
                    <div className="bg-teal-50 p-5 rounded-lg border-2 border-blue-100">
                      <div className="text-base font-bold uppercase font-semibold text-blue-700">Energy Opportunity</div>
                      <div className="text-xl lg:text-2xl font-bold font-bold text-blue-700">{opp.energy_opportunity_kwh} {opp.category === 'STARTUP_OVERLAP' ? 'kW (Peak)' : 'kWh'}</div>
                    </div>
                  </div>
                </div>
                
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
