
      {/* 5. ALERTS & ECONOMICS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-6 border-t border-slate-200">
         <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <h3 className="text-xs font-black tracking-widest uppercase text-slate-800 mb-6 border-b border-slate-100 pb-2">Active Alerts & System Events</h3>
            <div className="space-y-3">
               {state.active_alerts && state.active_alerts.length > 0 ? state.active_alerts.map((a:any, i:number) => (
                  <div key={i} className="flex gap-4 items-center p-3 border border-red-200 bg-red-50 text-red-900 rounded text-xs">
                     <div className="w-2 h-2 rounded-full bg-red-600 animate-pulse"></div>
                     <div className="font-bold flex-1">{a.message || a.id}</div>
                     <div className="text-[9px] font-bold tracking-widest">{new Date(a.timestamp).toLocaleTimeString()}</div>
                  </div>
               )) : (
                  <div className="text-sm text-slate-400">No active alerts. Factory operating within safe parameters.</div>
               )}
            </div>
         </div>
         <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <h3 className="text-xs font-black tracking-widest uppercase text-slate-800 mb-6 border-b border-slate-100 pb-2">Energy Economics (Business Impact)</h3>
            <div className="grid grid-cols-2 gap-6">
               <div>
                  <div className="text-[9px] text-slate-400 uppercase font-bold tracking-widest mb-1">Energy Cost (Measured)</div>
                  <div className="text-xl font-black text-slate-700">₹{state.cost_today_inr?.toFixed(0) || 0}</div>
               </div>
               <div>
                  <div className="text-[9px] text-slate-400 uppercase font-bold tracking-widest mb-1">Demand Penalty Risk (Projected)</div>
                  <div className="text-xl font-black text-slate-700">₹{(risk === 'CRITICAL' ? 15000 : 0).toLocaleString()}</div>
               </div>
            </div>
            <div className="mt-4 pt-4 border-t border-slate-100 flex justify-between items-center text-xs">
               <span className="text-slate-500 font-bold uppercase tracking-widest text-[9px]">Optimization Savings Potential</span>
               <span className="font-black text-green-600">₹{pipeline?.optimization?.scenarios?.length > 0 ? 15000 : 0} / month</span>
            </div>
         </div>
      </div>
