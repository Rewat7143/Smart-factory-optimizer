import re

file_path = 'frontend/app/forecast/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

pattern1 = r'(\{historyData \? \(\n\s*)(\{forecasts\.length === 0)'
replacement1 = r'\1<>\n\s*\2'
content = re.sub(pattern1, replacement1, content)

pattern2 = r'(style=\{\{ height: \'100\%\', width: \'100\%\' \}\} \n\s*\/>\n\s*)(\) : \()'
replacement2 = r'\1</>\n\s*\2'
content = re.sub(pattern2, replacement2, content)

with open(file_path, 'w') as f:
    f.write(content)
