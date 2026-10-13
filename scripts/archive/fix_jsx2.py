file_path = 'frontend/app/forecast/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

pattern1 = '''{historyData ? (
                     {forecasts.length === 0 && !isOffline && ('''
replacement1 = '''{historyData ? (
                     <>
                     {forecasts.length === 0 && !isOffline && ('''
content = content.replace(pattern1, replacement1)

pattern2 = '''                        style={{ height: '100%', width: '100%' }} 
                     />
                 ) : ('''
replacement2 = '''                        style={{ height: '100%', width: '100%' }} 
                     />
                     </>
                 ) : ('''
content = content.replace(pattern2, replacement2)

with open(file_path, 'w') as f:
    f.write(content)
