import re

file_path = 'frontend/components/LiveTelemetryDashboard.tsx'
with open(file_path, 'r') as f:
    content = f.read()

pattern = r"xAxis: \{\s*type: 'category',\s*data: recentChartData.map\(d => d.time\),\s*axisLabel: \{ color: '#64748b', fontWeight: 'bold' \}\s*\},\s*yAxis: \{\s*type: 'value',\s*name: 'Power \(kW\)',\s*axisLabel: \{ color: '#64748b' \}\s*\}"

replacement = """xAxis: { 
                     type: 'category', 
                     name: 'Time (IST)',
                     nameLocation: 'middle',
                     nameGap: 30,
                     nameTextStyle: { fontWeight: 'bold' },
                     data: recentChartData.map(d => d.time), 
                     axisLabel: { color: '#64748b', fontWeight: 'bold' } 
                 },
                 yAxis: { 
                     type: 'value', 
                     name: 'Active Power (kW)', 
                     nameLocation: 'middle',
                     nameGap: 50,
                     nameTextStyle: { fontWeight: 'bold' },
                     axisLabel: { color: '#64748b' } 
                 }"""

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

legend_pattern = r"tooltip: \{ trigger: 'axis' \},"
legend_replacement = "tooltip: { trigger: 'axis' },\n                 legend: { data: ['Live Power'], bottom: 0, textStyle: { fontWeight: 'bold' } },"
content = content.replace(legend_pattern, legend_replacement)

with open(file_path, 'w') as f:
    f.write(content)

