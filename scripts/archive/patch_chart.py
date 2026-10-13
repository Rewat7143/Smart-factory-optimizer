import re

file_path = 'frontend/app/forecast/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

chart_logic = r'  const timestamps = \[\.\.\.actuals\.map\(\(d:any\)=>d\.timestamp\), \.\.\.forecasts\.map\(\(d:any\)=>d\.timestamp\)\]\n  const actualData = actuals\.map\(\(d:any\)=>d\.power_kw\)\n  const forecastData = \[\.\.\.Array\(actuals\.length\)\.fill\(null\), \.\.\.forecasts\.map\(\(d:any\)=>d\.predicted_kw\)\]'

new_chart_logic = """  const timestamps = [...actuals.map((d:any)=>d.timestamp), ...forecasts.map((d:any)=>d.timestamp)]
  const actualData = [...actuals.map((d:any)=>d.power_kw), ...Array(forecasts.length).fill(null)]
  
  // To visually connect without faking an actual observation, we anchor the forecast series to the last actual observation
  const lastActualVal = actuals.length > 0 ? actuals[actuals.length - 1].power_kw : null
  const forecastData = [...Array(Math.max(0, actuals.length - 1)).fill(null), lastActualVal, ...forecasts.map((d:any)=>d.predicted_kw)]"""

content = re.sub(chart_logic, new_chart_logic, content, flags=re.DOTALL)

# Add explicit titles to the axes
chart_option = r"xAxis: \{ type: 'category', data: timestamps, axisLabel: \{ formatter: \(val: string\) => val \? \(val\.includes\('T'\) \? val\.split\('T'\)\[1\]\.substring\(0,5\) : String\(val\)\.substring\(0,10\)\) : '', color: '#334155' \} \},\n    yAxis: \{ type: 'value', name: 'Power \(kW\)', axisLabel: \{ color: '#334155' \} \},"
new_chart_option = """xAxis: { type: 'category', name: 'Time (IST)', nameLocation: 'middle', nameGap: 30, data: timestamps, axisLabel: { formatter: (val: string) => val ? (val.includes('T') ? val.split('T')[1].substring(0,5) : String(val).substring(0,10)) : '', color: '#334155' } },
    yAxis: { type: 'value', name: 'Active Power (kW)', nameLocation: 'middle', nameGap: 50, axisLabel: { color: '#334155' } },"""
content = content.replace(chart_option, new_chart_option)

# Add legend configuration
tooltip_option = r"tooltip: \{ trigger: 'axis' \},"
new_tooltip_option = "tooltip: { trigger: 'axis' },\n    legend: { data: ['Actual Demand', 'Forecast', 'Safe Limit'], bottom: 0 },"
content = content.replace(tooltip_option, new_tooltip_option)

with open(file_path, 'w') as f:
    f.write(content)
