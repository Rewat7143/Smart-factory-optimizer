with open('frontend/components/CommandCenter.tsx', 'r') as f:
    content = f.read()

# We need to import ReactECharts at the top if it's not there
if 'import ReactECharts' not in content:
    content = content.replace("import React, { useEffect, useState } from 'react'", "import React, { useEffect, useState } from 'react'\nimport ReactECharts from 'echarts-for-react'")

graphs_jsx = '''
      {/* EXECUTIVE GRAPHS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
         <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <div className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-6 border-b border-slate-200 pb-2">Peak Demand & Forecast Profile</div>
            <ReactECharts 
               style={{ height: '350px' }}
               option={{
                  animation: false,
                  tooltip: { trigger: 'axis' },
                  legend: { data: ['Actual (With AI)', 'Forecast', 'Without AI'], bottom: 0 },
                  xAxis: { type: 'category', data: ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00'], axisLabel: { color: '#64748b', fontWeight: 'bold' } },
                  yAxis: { type: 'value', name: 'kW', axisLabel: { color: '#64748b' } },
                  series: [
                     { name: 'Actual (With AI)', type: 'line', data: [310, 325, 340, 382, 360, 315], smooth: true, lineStyle: { color: '#0f766e', width: 4 }, itemStyle: { color: '#0f766e' } },
                     { name: 'Forecast', type: 'line', data: [None, None, None, 382, 360, 315], smooth: true, lineStyle: { color: '#9333ea', width: 3, type: 'dashed' } },
                     { name: 'Without AI', type: 'line', data: [310, 335, 360, 425, 390, 340], smooth: true, lineStyle: { color: '#ef4444', width: 2, type: 'dotted' } }
                  ],
                  grid: { left: '5%', right: '5%', top: '10%', bottom: '15%', containLabel: true }
               }} 
            />
         </div>
         <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <div className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-6 border-b border-slate-200 pb-2">Energy Cost Breakdown</div>
            <ReactECharts 
               style={{ height: '350px' }}
               option={{
                  animation: false,
                  tooltip: { trigger: 'item' },
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
                        data: [
                           { value: 12840, name: 'Production', itemStyle: { color: '#059669' } },
                           { value: 4280, name: 'Compressors', itemStyle: { color: '#0f766e' } },
                           { value: 3410, name: 'HVAC', itemStyle: { color: '#4f46e5' } },
                           { value: 2190, name: 'Pumping', itemStyle: { color: '#475569' } },
                           { value: 2100, name: 'Avoidable Waste', itemStyle: { color: '#dc2626' } }
                        ]
                     }
                  ]
               }} 
            />
         </div>
      </div>
'''

# Insert the graphs right before the "Closed-Loop Actions Today" (HOW WE DID IT) section
content = content.replace('{/* HOW WE DID IT */}', graphs_jsx + '\n      {/* HOW WE DID IT */}')

with open('frontend/components/CommandCenter.tsx', 'w') as f:
    f.write(content)
