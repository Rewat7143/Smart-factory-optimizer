"use client"
import React, { useState, useEffect } from 'react'

export default function DigitalTwin() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let isMounted = true
    const fetchState = async () => {
      try {
        const res = await fetch(`${(typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))}/digital-twin/state`)
        if (res.ok && isMounted) {
          setData(await res.json())
          setLoading(false)
        }
      } catch (e) {}
    }
    fetchState()
    const interval = setInterval(fetchState, 2000)
    return () => { isMounted = false; clearInterval(interval) }
  }, [])

  // Aggregate metrics dummy calculation if not provided by API
  const totalLoad = data?.topology?.reduce((acc: number, asset: any) => acc + (asset.power_kw || 0), 0) || 0;
  const highRisk = data?.risk_timeline?.some((t: any) => t.risk_level === 'HIGH');

  // Categorize nodes
  const productionNodes = data?.topology?.filter((a: any) => ['PRODUCTION', 'ASSEMBLY', 'MACHINE'].includes(a.category?.toUpperCase()) || !a.category) || [];
  const utilityNodes = data?.topology?.filter((a: any) => ['UTILITY', 'HVAC', 'STORAGE', 'BATTERY'].includes(a.category?.toUpperCase())) || [];

  return (
    
      <div className="max-w-[1600px] mx-auto space-y-6 font-mono text-slate-800 pb-20">
        {highRisk && (
          <div className="bg-red-600 text-white text-slate-800 p-5 text-center uppercase tracking-widest font-bold text-lg font-bold animate-pulse rounded-xl shadow-sm mb-4">
            WARNING: HIGH RISK STATE DETECTED IN TIMELINE
          </div>
        )}
        <div className="flex justify-between items-end border-b border-slate-200 pb-4">
          <div>
            <h1 className="text-xl lg:text-2xl font-bold font-bold tracking-tight text-slate-800 uppercase">FACTORY DIGITAL TWIN</h1>
            <p className="text-base font-bold text-slate-800 uppercase tracking-widest font-bold mt-1">Live Energy Topology</p>
          </div>
        </div>

        {loading ? (
           <div className="p-10 font-mono text-slate-800">INITIALIZING TWIN...</div>
        ) : (
           <div className="space-y-6">
              {/* Top Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                 <div className="bg-white border-2 border-slate-200 rounded-xl shadow-sm p-4">
                    <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800 mb-2">Total Load</div>
                    <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">{data?.metrics?.total_load_kw || totalLoad} <span className="text-base font-bold">kW</span></div>
                 </div>
                 <div className="bg-white border-2 border-slate-200 rounded-xl shadow-sm p-4">
                    <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800 mb-2">Contract Demand</div>
                    <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">{data?.metrics?.contract_demand_kw || 0} <span className="text-base font-bold">kW</span></div>
                 </div>
                 <div className="bg-white border-2 border-slate-200 rounded-xl shadow-sm p-4">
                    <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800 mb-2">Headroom</div>
                    <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">{data?.metrics?.headroom_kw || 0} <span className="text-base font-bold">kW</span></div>
                 </div>
                 <div className="bg-white border-2 border-slate-200 rounded-xl shadow-sm p-4">
                    <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800 mb-2">Load Factor</div>
                    <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">{data?.metrics?.load_factor_percent || 0} <span className="text-base font-bold">%</span></div>
                 </div>
              </div>

              {/* Power Balance Breakdown */}
              <div className="bg-white border-2 border-slate-200 rounded-xl shadow-sm p-4">
                 <h3 className="text-base font-bold font-bold uppercase tracking-widest text-slate-800 mb-4">Power Balance Breakdown</h3>
                 <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    {data?.power_balance ? Object.entries(data.power_balance).map(([key, val]: any) => (
                      <div key={key}>
                        <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800">{key.replace('_kw', '').replace('_', ' ')} kW</div>
                        <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">{val}</div>
                      </div>
                    )) : (
                      <>
                        <div>
                          <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800">Production kW</div>
                          <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">0</div>
                        </div>
                        <div>
                          <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800">Utility kW</div>
                          <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">0</div>
                        </div>
                        <div>
                          <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800">HVAC kW</div>
                          <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">0</div>
                        </div>
                        <div>
                          <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800">Auxiliary kW</div>
                          <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">0</div>
                        </div>
                        <div>
                          <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800">Storage kW</div>
                          <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">0</div>
                        </div>
                      </>
                    )}
                 </div>
              </div>

              {/* Topology Grid */}
              <div className="space-y-6">
                <div>
                  <h3 className="text-base font-bold font-bold uppercase tracking-widest text-slate-700 mb-4">Production Assets</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                     {(productionNodes.length ? productionNodes : data?.topology || [])?.map((asset: any) => (
                        <div key={asset.id} className={`border-2 rounded-xl p-5 shadow-sm bg-white relative overflow-hidden ${asset.criticality === 'CRITICAL' ? 'border-red-300' : asset.criticality === 'FLEXIBLE' ? 'border-blue-300' : 'border-amber-300'}`}>
                           
                           <div className="flex justify-between items-start mb-4">
                              <div>
                                 <div className="text-lg font-bold font-bold text-slate-800">{asset.name}</div>
                                 <div className="text-lg font-bold font-bold text-slate-800 uppercase tracking-widest">{asset.category}</div>
                              </div>
                              <div className={`px-2 py-1 rounded text-lg font-bold font-bold font-bold tracking-widest uppercase ${asset.status === 'FAULT' ? 'bg-red-100 text-red-700' : asset.status === 'RUNNING' ? 'bg-green-100 text-green-700' : 'bg-slate-50 text-slate-700'}`}>
                                 {asset.status}
                              </div>
                           </div>

                           <div className="space-y-4 mb-4">
                              <div>
                                 <div className="flex justify-between text-base font-bold uppercase font-bold text-slate-800 mb-1">
                                    <span>Load</span>
                                    <span>{asset.load_percent}%</span>
                                 </div>
                                 <div className="w-full bg-slate-50 rounded-full h-2">
                                    <div className={`h-2 rounded-full bg-slate-50`} style={{ width: `${asset.load_percent}%` }}></div>
                                 </div>
                              </div>
                              <div className="grid grid-cols-2 gap-4">
                                 <div className="bg-slate-50 p-2 rounded border-2 border-slate-100">
                                    <div className="text-lg font-bold font-bold uppercase font-bold text-slate-800 mb-1">Power</div>
                                    <div className="text-base font-bold font-bold text-slate-700">{asset.power_kw} <span className="text-lg font-bold font-bold text-slate-800">kW</span></div>
                                 </div>
                                 <div className="bg-slate-50 p-2 rounded border-2 border-slate-100">
                                    <div className="text-lg font-bold font-bold uppercase font-bold text-slate-800 mb-1">Criticality</div>
                                    <div className={`text-base font-bold font-bold ${asset.criticality === 'CRITICAL' ? 'text-red-600' : asset.criticality === 'FLEXIBLE' ? 'text-teal-700' : 'text-amber-600'}`}>{asset.criticality}</div>
                                 </div>
                              </div>
                           </div>
                        </div>
                     ))}
                  </div>
                </div>

                {utilityNodes.length > 0 && (
                  <div>
                    <h3 className="text-base font-bold font-bold uppercase tracking-widest text-slate-700 mb-4">Utility & Support Assets</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                       {utilityNodes.map((asset: any) => (
                          <div key={asset.id} className={`border-2 rounded-xl p-5 shadow-sm bg-white relative overflow-hidden ${asset.criticality === 'CRITICAL' ? 'border-red-300' : asset.criticality === 'FLEXIBLE' ? 'border-blue-300' : 'border-amber-300'}`}>
                             
                             <div className="flex justify-between items-start mb-4">
                                <div>
                                   <div className="text-lg font-bold font-bold text-slate-800">{asset.name}</div>
                                   <div className="text-lg font-bold font-bold text-slate-800 uppercase tracking-widest">{asset.category}</div>
                                </div>
                                <div className={`px-2 py-1 rounded text-lg font-bold font-bold font-bold tracking-widest uppercase ${asset.status === 'FAULT' ? 'bg-red-100 text-red-700' : asset.status === 'RUNNING' ? 'bg-green-100 text-green-700' : 'bg-slate-50 text-slate-700'}`}>
                                   {asset.status}
                                </div>
                             </div>

                             <div className="space-y-4 mb-4">
                                <div>
                                   <div className="flex justify-between text-base font-bold uppercase font-bold text-slate-800 mb-1">
                                      <span>Load</span>
                                      <span>{asset.load_percent}%</span>
                                   </div>
                                   <div className="w-full bg-slate-50 rounded-full h-2">
                                      <div className={`h-2 rounded-full bg-slate-50`} style={{ width: `${asset.load_percent}%` }}></div>
                                   </div>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                   <div className="bg-slate-50 p-2 rounded border-2 border-slate-100">
                                      <div className="text-lg font-bold font-bold uppercase font-bold text-slate-800 mb-1">Power</div>
                                      <div className="text-base font-bold font-bold text-slate-700">{asset.power_kw} <span className="text-lg font-bold font-bold text-slate-800">kW</span></div>
                                   </div>
                                   <div className="bg-slate-50 p-2 rounded border-2 border-slate-100">
                                      <div className="text-lg font-bold font-bold uppercase font-bold text-slate-800 mb-1">Criticality</div>
                                      <div className={`text-base font-bold font-bold ${asset.criticality === 'CRITICAL' ? 'text-red-600' : asset.criticality === 'FLEXIBLE' ? 'text-teal-700' : 'text-amber-600'}`}>{asset.criticality}</div>
                                   </div>
                                </div>
                             </div>
                          </div>
                       ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Risk Timeline */}
              <div className="bg-white border-2 border-slate-200 rounded-xl shadow-sm p-4">
                 <h3 className="text-base font-bold font-bold uppercase tracking-widest text-slate-800 mb-4">Risk Timeline Forecast</h3>
                 <div className="flex gap-4">
                    {data?.risk_timeline?.map((rt: any, idx: number) => (
                      <div key={idx} className="flex-1 bg-slate-50 p-4 rounded border-2 border-slate-100 text-center">
                        <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800 mb-2">+{rt.time_offset_min} MIN</div>
                        <div className={`text-lg font-bold font-bold uppercase tracking-widest ${rt.risk_level === 'HIGH' ? 'text-red-600' : rt.risk_level === 'MEDIUM' ? 'text-amber-500' : 'text-green-600'}`}>{rt.risk_level}</div>
                      </div>
                    ))}
                    {!data?.risk_timeline && [5, 10, 15].map(t => (
                      <div key={t} className="flex-1 bg-slate-50 p-4 rounded border-2 border-slate-100 text-center">
                        <div className="text-lg font-bold font-bold uppercase tracking-widest font-bold text-slate-800 mb-2">+{t} MIN</div>
                        <div className="text-lg font-bold font-bold uppercase tracking-widest text-slate-800">NO DATA</div>
                      </div>
                    ))}
                 </div>
              </div>

           </div>
        )}
      </div>
    
  )
}
