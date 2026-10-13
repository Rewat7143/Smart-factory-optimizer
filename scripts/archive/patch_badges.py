import re

# 1. Forecast Page
file_path = 'frontend/app/forecast/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

badge_logic = """<div className="flex items-center justify-end gap-2 text-sm font-bold tracking-widest">
                {state.live_status === 'CONNECTED_TEST' ? (
                   <><div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div> <span className="text-amber-600">RASPBERRY PI TEST STREAM</span></>
                ) : state.live_status === 'CONNECTED' ? (
                   <><div className="w-2 h-2 rounded-full bg-teal-600 animate-pulse"></div> <span className="text-teal-700">RASPBERRY PI / L&T METER CONNECTED</span></>
                ) : (
                   <><div className="w-2 h-2 rounded-full bg-slate-400"></div> <span className="text-slate-500">METER OFFLINE</span></>
                )}
             </div>"""

content = re.sub(r'<div className="flex items-center justify-end gap-2 text-teal-700 text-sm font-bold tracking-widest">\s*<div className="w-2 h-2 rounded-full bg-teal-600 animate-pulse"></div> LIVE FACTORY TELEMETRY\s*</div>', badge_logic, content)

with open(file_path, 'w') as f:
    f.write(content)


# 2. LiveTelemetryDashboard (Boardroom)
file_path2 = 'frontend/components/LiveTelemetryDashboard.tsx'
with open(file_path2, 'r') as f:
    content2 = f.read()
    
# In LiveTelemetryDashboard, `status` comes from `/telemetry/source-status` directly.
# The `active_source` will be 'SIMULATED_RASPI', 'RASPBERRY_PI', or 'NONE'.
badge_logic2 = """{status?.active_source === 'SIMULATED_RASPI' ? (
                <><div className="w-3 h-3 rounded-full bg-amber-500 animate-pulse mr-2"></div><span className="text-amber-600">RASPBERRY PI TEST STREAM</span></>
             ) : status?.active_source === 'RASPBERRY_PI' ? (
                <><div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse mr-2"></div><span className="text-emerald-700">RASPBERRY PI / L&T METER CONNECTED</span></>
             ) : (
                <><div className="w-3 h-3 rounded-full bg-slate-400 mr-2"></div><span className="text-slate-600">METER OFFLINE</span></>
             )}"""
             
content2 = re.sub(r'\{isOffline \? \(\s*<><div className="w-3 h-3 rounded-full bg-slate-400 mr-2"></div><span className="text-slate-600">OFFLINE</span></>\s*\) : \(\s*<><div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse mr-2"></div><span className="text-emerald-700">LIVE METER CONNECTED</span></>\s*\)\}', badge_logic2, content2)

with open(file_path2, 'w') as f:
    f.write(content2)

