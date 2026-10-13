import re

file_path = 'frontend/app/telemetry/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

replacement = "yAxis: { type: 'value', name: 'Voltage (V)', scale: true, axisLabel: { color: '#64748b', fontWeight: 'bold' }, nameTextStyle: { fontWeight: 'bold' } },"

pattern = r'yAxis: \{ type: \'value\', name: \'Voltage \(V\)\', min: 380, max: 440, axisLabel: \{ color: \'#64748b\', fontWeight: \'bold\' \}, nameTextStyle: \{ fontWeight: \'bold\' \} \},'
content = re.sub(pattern, replacement, content)

with open(file_path, 'w') as f:
    f.write(content)
