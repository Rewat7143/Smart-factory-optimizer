import re

file_path = 'frontend/components/CommandCenter.tsx'
with open(file_path, 'r') as f:
    content = f.read()

pattern = r'\{ value: Math\.round\(historyData\.categories\.Production \* 7\.5\), name: \'Production\''
replacement = r'{ value: Math.round((historyData.categories?.Production || 0) * 7.5), name: \'Production\''
content = re.sub(pattern, replacement, content)

pattern = r'\{ value: Math\.round\(historyData\.categories\.Utility \* 7\.5\), name: \'Compressors\''
replacement = r'{ value: Math.round((historyData.categories?.Utility || 0) * 7.5), name: \'Compressors\''
content = re.sub(pattern, replacement, content)

pattern = r'\{ value: Math\.round\(historyData\.categories\.HVAC \* 7\.5\), name: \'HVAC\''
replacement = r'{ value: Math.round((historyData.categories?.HVAC || 0) * 7.5), name: \'HVAC\''
content = re.sub(pattern, replacement, content)

pattern = r'\{ value: Math\.round\(historyData\.categories\.Auxiliary \* 7\.5\), name: \'Pumping & Aux\''
replacement = r'{ value: Math.round((historyData.categories?.Auxiliary || 0) * 7.5), name: \'Pumping & Aux\''
content = re.sub(pattern, replacement, content)

with open(file_path, 'w') as f:
    f.write(content)
