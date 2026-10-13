import re

file_path = 'frontend/app/forecast/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

pattern = r'const chartOption = \{.*?grid: \{ left: \'3%\', right: \'4%\', bottom: \'3%\', containLabel: true \}\n  \}'

replacement = """const chartOption = {
    animation: false,
    tooltip: { trigger: 'axis' },
    legend: { data: ['Actual Demand', 'Forecast', 'Safe Limit'], bottom: 0, textStyle: { fontWeight: 'bold' } },
    xAxis: { type: 'category', name: 'Time (IST)', nameLocation: 'middle', nameGap: 30, nameTextStyle: { fontWeight: 'bold' }, data: timestamps, axisLabel: { formatter: (val: string) => val ? (val.includes('T') ? val.split('T')[1].substring(0,5) : String(val).substring(0,10)) : '', color: '#334155' } },
    yAxis: { type: 'value', name: 'Active Power (kW)', nameLocation: 'middle', nameGap: 50, nameTextStyle: { fontWeight: 'bold' }, axisLabel: { color: '#334155' } },
    series: [
      { name: 'Actual Demand', type: 'line', data: isOffline ? [] : actualData, smooth: true, showSymbol: false, lineStyle: { color: '#0f766e', width: 3 } },
      { name: 'Forecast', type: 'line', data: isOffline ? [] : forecastData, smooth: true, showSymbol: false, lineStyle: { color: '#9333ea', width: 3, type: 'dashed' } },
      { name: 'Safe Limit', type: 'line', data: isOffline ? [] : Array(timestamps.length).fill(state?.contract_demand_kw || 100), showSymbol: false, lineStyle: { color: '#dc2626', width: 2, type: 'dotted' } }
    ],
    grid: { left: '3%', right: '5%', bottom: '15%', top: '10%', containLabel: true }
  }"""

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

