import re

file_path = 'frontend/app/forecast/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

# Add a warning overlay if forecast is empty and we're in live mode
pattern = r'<ReactECharts.*?style=\{\{ height: \'400px\' \}\}'

replacement = """{forecasts.length === 0 && !isOffline && (
            <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/50 backdrop-blur-sm rounded-xl">
               <div className="bg-white border-2 border-slate-300 p-4 rounded-lg shadow-lg font-bold text-slate-700">
                  INSUFFICIENT LIVE HISTORY FOR FORECASTING
               </div>
            </div>
        )}
        <ReactECharts 
              style={{ height: '400px' }}"""

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# We also need to add `relative` to the container so the overlay works.
container_pattern = r'<div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">'
container_replacement = '<div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 relative">'
content = content.replace(container_pattern, container_replacement)

with open(file_path, 'w') as f:
    f.write(content)
