import re

file_path = 'frontend/app/forecast/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

# Find the inline option={{...}} and replace it with option={chartOption}
# Wait, chartOption is already defined at the top:
# const chartOption = { ... }

# Let's replace the <ReactECharts option={{...}} style=...> with <ReactECharts option={chartOption} style=...>
pattern = r'<ReactECharts \s*option=\{\{.*?(?:grid: \{ left: \'8%\'.*?\}\s*)\}\}\s*style=\{\{ height: \'100%\', width: \'100%\' \}\} \s*/>'
replacement = '<ReactECharts option={chartOption} style={{ height: "100%", width: "100%" }} />'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
