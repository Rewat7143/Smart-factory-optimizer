"use client"
export default function FleetPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-6 font-mono">
       <div className="bg-white text-slate-800 p-4 rounded-xl border-2 border-slate-200 shadow flex justify-between items-center">
          <div>
             <h1 className="text-xl lg:text-2xl font-bold font-bold uppercase tracking-widest text-teal-500">Fleet Command Center</h1>
             <p className="text-lg font-bold text-slate-800 mt-1">Enterprise-scale visibility across all connected manufacturing plants.</p>
          </div>
       </div>

       <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-4 rounded-xl border-2 border-slate-200 shadow-sm">
             <div className="text-base font-bold font-bold text-slate-800 uppercase tracking-widest mb-2">Connected Factories</div>
             <div className="text-xl lg:text-xl lg:text-2xl font-bold font-bold text-slate-800">4 / 4</div>
          </div>
          <div className="bg-white p-4 rounded-xl border-2 border-slate-200 shadow-sm">
             <div className="text-base font-bold font-bold text-slate-800 uppercase tracking-widest mb-2">Fleet Active Demand</div>
             <div className="text-xl lg:text-xl lg:text-2xl font-bold font-bold text-slate-800">124.5 <span className="text-lg font-bold">MW</span></div>
          </div>
          <div className="bg-white p-4 rounded-xl border-2 border-slate-200 shadow-sm">
             <div className="text-base font-bold font-bold text-slate-800 uppercase tracking-widest mb-2">Active Alerts</div>
             <div className="text-xl lg:text-xl lg:text-2xl font-bold font-bold text-red-600">2</div>
          </div>
          <div className="bg-white p-4 rounded-xl border-2 border-slate-200 shadow-sm">
             <div className="text-base font-bold font-bold text-slate-800 uppercase tracking-widest mb-2">Opt Opportunities</div>
             <div className="text-xl lg:text-xl lg:text-2xl font-bold font-bold text-green-600">3</div>
          </div>
       </div>

       <div className="bg-white rounded-xl shadow-sm border-2 border-slate-200 overflow-hidden">
          <table className="w-full text-left text-lg font-bold">
             <thead className="bg-slate-50 border-b border-slate-200 text-base font-bold text-slate-800 uppercase tracking-widest">
                <tr>
                   <th className="p-4">Facility</th>
                   <th className="p-4">Region</th>
                   <th className="p-4">Current Demand</th>
                   <th className="p-4">Peak Risk</th>
                   <th className="p-4">AI Status</th>
                   <th className="p-4">Action Required</th>
                </tr>
             </thead>
             <tbody className="divide-y divide-slate-100">
                <tr className="hover:bg-slate-50 bg-teal-50/20">
                   <td className="p-4 font-bold text-blue-700">Plant Alpha</td>
                   <td className="p-4 text-slate-800">APAC (India)</td>
                   <td className="p-4 font-mono font-bold">128.4 kW</td>
                   <td className="p-4"><span className="px-2 py-1 bg-red-100 text-red-700 rounded text-base font-bold font-bold animate-pulse">HIGH</span></td>
                   <td className="p-4 text-green-600 font-bold">OPTIMIZED</td>
                   <td className="p-4"><button className="px-3 py-1 bg-teal-700 text-white text-slate-800 rounded text-base font-bold font-bold uppercase hover:bg-blue-700">Review</button></td>
                </tr>
                <tr className="hover:bg-slate-50">
                   <td className="p-4 font-bold text-slate-700">Plant Beta</td>
                   <td className="p-4 text-slate-800">EMEA (Germany)</td>
                   <td className="p-4 font-mono font-bold">42.1 MW</td>
                   <td className="p-4"><span className="px-2 py-1 bg-green-100 text-green-700 rounded text-base font-bold font-bold">LOW</span></td>
                   <td className="p-4 text-slate-800 font-bold">MONITORING</td>
                   <td className="p-4 text-slate-800">-</td>
                </tr>
                <tr className="hover:bg-slate-50 bg-orange-50/20">
                   <td className="p-4 font-bold text-slate-700">Plant Gamma</td>
                   <td className="p-4 text-slate-800">AMER (Texas)</td>
                   <td className="p-4 font-mono font-bold">14.2 MW</td>
                   <td className="p-4"><span className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-base font-bold font-bold">WARNING</span></td>
                   <td className="p-4 text-slate-800 font-bold">MONITORING</td>
                   <td className="p-4 text-slate-800">-</td>
                </tr>
                <tr className="hover:bg-slate-50 bg-slate-50/50 text-slate-800">
                   <td className="p-4 font-bold text-slate-800">Plant Delta</td>
                   <td className="p-4 text-slate-800">APAC (Japan)</td>
                   <td className="p-4 font-mono font-bold">--</td>
                   <td className="p-4"><span className="px-2 py-1 bg-slate-200 text-slate-800 rounded text-base font-bold font-bold">UNKNOWN</span></td>
                   <td className="p-4 text-red-500 font-bold">METER OFFLINE</td>
                   <td className="p-4 text-red-500 font-bold">INVESTIGATE</td>
                </tr>
             </tbody>
          </table>
       </div>
    </div>
  )
}
