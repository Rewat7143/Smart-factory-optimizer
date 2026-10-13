import re

file_path = 'frontend/app/forecast/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """{forecasts.length === 0 && !isOffline && (
            <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/50 backdrop-blur-sm rounded-xl">
               <div className="bg-white border-2 border-slate-300 p-4 rounded-lg shadow-lg font-bold text-slate-700">
                  INSUFFICIENT LIVE HISTORY FOR FORECASTING
               </div>
            </div>
        )}
        <ReactECharts"""

content = content.replace("<ReactECharts", replacement, 1)

with open(file_path, 'w') as f:
    f.write(content)
