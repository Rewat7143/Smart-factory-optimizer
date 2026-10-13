import re

with open('frontend/app/forecast/page.tsx', 'r') as f:
    content = f.read()

# Replace the entire return statement
return_block = re.search(r'return \(\n      <div.*$', content, re.DOTALL).group(0)

new_ui = '''return (
      <div className="max-w-[1600px] mx-auto space-y-6 font-mono text-slate-800 pb-20 p-6">
        
        {/* HEADER */}
        <div className="flex justify-between items-end border-b border-slate-300 pb-4">
          <div>
            <h1 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-800 uppercase">Energy Intelligence</h1>
            <p className="text-sm font-semibold tracking-widest text-slate-500 uppercase mt-2">AI-Driven Peak Prediction & Anomaly Detection</p>
          </div>
          <div className="text-right">
             <div className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-1">Data Source</div>
             <div className="flex items-center justify-end gap-2 text-teal-700 text-sm font-bold tracking-widest">
                <div className="w-2 h-2 rounded-full bg-teal-600 animate-pulse"></div> LIVE FACTORY TELEMETRY
             </div>
          </div>
        </div>

        {/* TOP STATUS STRIP */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
           {[
             { label: 'Current Demand', value: isOffline ? '#### kW' : `${(pipeline?.pipeline?.current_demand || 0).toFixed(1)} kW`, color: 'text-slate-800' },
             { label: 'Predicted Peak (15m)', value: isOffline ? '#### kW' : `${(pipeline?.pipeline?.predicted_peak || 0).toFixed(1)} kW`, color: 'text-purple-700' },
             { label: 'Demand Limit', value: isOffline ? '#### kW' : `${(pipeline?.pipeline?.safe_target || 0).toFixed(1)} kW`, color: 'text-red-600' },
             { label: 'Peak Headroom', value: isOffline ? '#### kW' : `${(pipeline?.pipeline?.headroom || 0).toFixed(1)} kW`, color: 'text-emerald-700' },
             { label: 'Peak Risk Status', value: isOffline ? '####' : pipeline?.pipeline?.peak_risk, color: pipeline?.pipeline?.peak_risk === 'HIGH' ? 'text-orange-600' : 'text-teal-700' }
           ].map((k, i) => (
             <div key={i} className="bg-slate-50 border border-slate-200 p-4 rounded-xl shadow-sm">
                <div className="text-xs font-semibold uppercase text-slate-500 tracking-widest mb-1">{k.label}</div>
                <div className={`text-2xl font-bold tracking-tight ${k.color}`}>{k.value}</div>
             </div>
           ))}
        </div>

        {/* MAIN VISUAL & ROOT CAUSE */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
           <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col">
              <div className="text-sm font-bold uppercase tracking-widest text-slate-800 mb-1">POWER DEMAND — ACTUAL vs FORECAST vs DEMAND LIMIT</div>
              <div className="text-xs font-semibold text-slate-500 mb-6 border-b border-slate-100 pb-2">Real factory demand compared with the 15-minute predicted peak and contracted limit.</div>
              
              <div className="flex-1 min-h-[400px]">
                 {historyData ? (
                     <ReactECharts 
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
                           xAxis: { type: 'category', data: historyData.timeline.slice(-48), name: 'Time (HH:MM)', axisLabel: { color: '#64748b', fontWeight: 'bold', formatter: (val: string) => val.split(' ')[1] || val }, nameTextStyle: { fontWeight: 'bold', padding: [0, 0, 0, 10] } },
                           yAxis: { type: 'value', name: 'Power Demand (kW)', axisLabel: { color: '#64748b' }, nameTextStyle: { fontWeight: 'bold', padding: [0, 0, 10, 0] }, min: (val: any) => Math.max(0, val.min - 20) },
                           series: [
                              { name: 'Actual Demand', type: 'line', data: isOffline ? [] : historyData.demand.slice(-48), smooth: false, showSymbol: false, lineStyle: { color: '#0f766e', width: 3 }, itemStyle: { color: '#0f766e' } },
                              { name: 'Demand Limit', type: 'line', data: isOffline ? [] : Array(48).fill(pipeline?.pipeline?.safe_target || 100), showSymbol: false, lineStyle: { color: '#ef4444', width: 2, type: 'dashed' }, itemStyle: { color: '#ef4444' } }
                           ],
                           grid: { left: '8%', right: '5%', top: '10%', bottom: '15%', containLabel: true }
                        }} 
                        style={{ height: '100%', width: '100%' }} 
                     />
                 ) : (
                     <div className="h-full flex items-center justify-center text-slate-400 font-bold tracking-widest">LOADING TELEMETRY...</div>
                 )}
              </div>
              
              <div className="mt-4 p-4 bg-slate-50 border border-slate-200 rounded-lg">
                 <div className="text-xs font-bold uppercase tracking-widest text-slate-800 mb-1">KEY INSIGHT</div>
                 <div className="text-sm font-semibold text-slate-600">
                    {isOffline ? 'System offline.' : (
                        pipeline?.pipeline?.peak_risk === 'HIGH' 
                           ? `Demand is approaching the contracted limit. The predicted peak of ${pipeline.pipeline.predicted_peak.toFixed(1)} kW leaves only ${pipeline.pipeline.headroom.toFixed(1)} kW of headroom.`
                           : `Demand is stable. The predicted peak of ${pipeline?.pipeline?.predicted_peak?.toFixed(1) || 0} kW is safely below the ${pipeline?.pipeline?.safe_target || 0} kW limit.`
                    )}
                 </div>
              </div>
           </div>

           <div className="lg:col-span-1 space-y-6">
              {/* ROOT CAUSE */}
              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                 <div className="text-sm font-bold uppercase tracking-widest text-slate-800 mb-1">Peak Demand Attribution</div>
                 <div className="text-xs font-semibold text-slate-500 mb-6 border-b border-slate-100 pb-2">Which assets are contributing most to the current peak?</div>
                 
                 {isOffline ? (
                     <div className="text-slate-500 font-bold">Waiting for telemetry...</div>
                 ) : (
                     <div className="space-y-4">
                         {(pipeline?.attribution || []).slice(0, 4).map((attr: any, i: number) => (
                            <div key={i} className="flex justify-between items-center text-sm font-bold">
                               <span className="text-slate-700">{attr.name}</span>
                               <span className="flex gap-4">
                                  <span className="text-slate-800">{attr.power.toFixed(1)} kW</span>
                                  <span className={`w-16 text-right ${attr.type === 'CRITICAL' ? 'text-red-600' : 'text-teal-600'}`}>{attr.type === 'CRITICAL' ? 'PROT' : 'FLEX'}</span>
                               </span>
                            </div>
                         ))}
                     </div>
                 )}
              </div>

              {/* RECOMMENDATION */}
              {!isOffline && pipeline?.optimization?.status === 'OPTIMIZED' && pipeline.optimization.actions.length > 0 && (
              <div className="bg-teal-50 border-l-4 border-teal-600 rounded-xl p-6 shadow-sm">
                 <div className="text-sm font-bold uppercase tracking-widest text-teal-800 mb-1">Optimization Impact</div>
                 <div className="text-xs font-semibold text-teal-600 mb-4 border-b border-teal-200 pb-2">BEFORE → ACTION → AFTER</div>
                 
                 <div className="text-sm font-bold text-slate-800 mb-4">{pipeline.optimization.actions[0].action}</div>
                 
                 <div className="grid grid-cols-2 gap-y-3 text-sm mb-4">
                    <div className="text-slate-500 font-semibold">Predicted Peak</div><div className="font-bold text-slate-800 text-right">{pipeline.pipeline.predicted_peak.toFixed(1)} kW</div>
                    <div className="text-slate-500 font-semibold">Optimized Peak</div><div className="font-bold text-teal-700 text-right">{pipeline.pipeline.safe_target.toFixed(1)} kW</div>
                    <div className="text-slate-500 font-semibold">Peak Avoided</div><div className="font-bold text-emerald-600 text-right">{(pipeline.pipeline.predicted_peak - pipeline.pipeline.safe_target).toFixed(1)} kW</div>
                    <div className="text-slate-500 font-semibold">Production Impact</div><div className="font-bold text-slate-800 text-right">0%</div>
                 </div>
              </div>
              )}
           </div>
        </div>

        <div className="mt-8 border-t border-slate-200 pt-6 flex justify-between items-center text-xs text-slate-500 font-semibold">
           <div>Report Generated by Factory Energy Autopilot Engine</div>
           <div>Data Source: {isOffline ? 'OFFLINE' : 'LIVE MODBUS RTU'}</div>
           <div>{new Date().toISOString().replace('T', ' ').substring(0, 19)} UTC</div>
        </div>
      </div>
  )
}'''

content = content.replace(return_block, new_ui)

with open('frontend/app/forecast/page.tsx', 'w') as f:
    f.write(content)
