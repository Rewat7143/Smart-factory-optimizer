import re

with open('frontend/components/CommandCenter.tsx', 'r') as f:
    content = f.read()

# Replace the Peak Demand & Forecast Profile chart
# We need to extract the exact JSX of the two charts and replace them.
# I'll use regex to find the EXECUTIVE GRAPHS block.

chart_block = re.search(r'\{\/\* EXECUTIVE GRAPHS \*\/\}.*?\{\/\* HOW WE DID IT \*\/\}', content, re.DOTALL).group(0)

new_charts = '''{/* EXECUTIVE GRAPHS */}
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
                           radius: ['40%', '70%'],
                           center: ['40%', '50%'],
                           avoidLabelOverlap: false,
                           itemStyle: { borderRadius: 5, borderColor: '#fff', borderWidth: 2 },
                           label: { show: false },
                           data: isOffline ? [] : [
                              { value: Math.round(historyData.categories.Production * 7.5), name: 'Production', itemStyle: { color: '#059669' } },
                              { value: Math.round(historyData.categories.Utility * 7.5), name: 'Compressors', itemStyle: { color: '#0f766e' } },
                              { value: Math.round(historyData.categories.HVAC * 7.5), name: 'HVAC', itemStyle: { color: '#4f46e5' } },
                              { value: Math.round(historyData.categories.Auxiliary * 7.5), name: 'Pumping & Aux', itemStyle: { color: '#475569' } }
                           ]
                        }
                     ]
                  }} 
               />
            ) : <div className="h-[350px] flex items-center justify-center text-slate-400 font-bold">LOADING TELEMETRY...</div>}
         </div>
      </div>
      {/* HOW WE DID IT */}'''

content = content.replace(chart_block, new_charts)

with open('frontend/components/CommandCenter.tsx', 'w') as f:
    f.write(content)
