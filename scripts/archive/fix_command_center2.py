file_path = 'frontend/components/CommandCenter.tsx'
with open(file_path, 'r') as f:
    content = f.read()

content = content.replace("name: \\'Production\\'", "name: 'Production'")
content = content.replace("name: \\'Compressors\\'", "name: 'Compressors'")
content = content.replace("name: \\'HVAC\\'", "name: 'HVAC'")
content = content.replace("name: \\'Pumping & Aux\\'", "name: 'Pumping & Aux'")

with open(file_path, 'w') as f:
    f.write(content)
