import re

file_path = 'frontend/app/forecast/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

# Make the legend names dynamic based on data_source
legend_logic = """const actualName = state.data_source === 'SIMULATED_RASPI' ? 'Actual — Raspberry Pi Test Stream' : (state.data_source === 'RASPBERRY_PI' ? 'Actual — Live Meter' : 'Actual Demand');
  const forecastName = state.data_source === 'SIMULATED_RASPI' ? 'Forecast — Test Stream' : 'Forecast';"""

# Insert before chartOption
content = content.replace("const chartOption = {", legend_logic + "\n  const chartOption = {")

# Update chartOption
content = content.replace("legend: { data: ['Actual Demand', 'Forecast', 'Safe Limit']", "legend: { data: [actualName, forecastName, 'Safe Limit']")
content = content.replace("{ name: 'Actual Demand', type: 'line',", "{ name: actualName, type: 'line',")
content = content.replace("{ name: 'Forecast', type: 'line',", "{ name: forecastName, type: 'line',")

with open(file_path, 'w') as f:
    f.write(content)
