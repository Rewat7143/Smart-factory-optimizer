import os
import re

files_to_patch = [
    'frontend/app/live-command/page.tsx',
    'frontend/app/live-twin/page.tsx',
    'frontend/app/live-quality/page.tsx',
    'frontend/app/live-economics/page.tsx',
    'frontend/app/live-copilot/page.tsx'
]

for file_path in files_to_patch:
    with open(file_path, 'r') as f:
        content = f.read()

    # 1. Remove LiveMeterPlaceholder import
    content = re.sub(r"import \{ LiveMeterPlaceholder \}.*\n", "", content)

    # 2. Find and remove the early return block:
    # if (error || !data) {
    #   return <LiveMeterPlaceholder />;
    # }
    early_return_pattern = re.compile(
        r"if\s*\(\s*error\s*\|\|\s*!data\s*\)\s*\{\s*return\s*<LiveMeterPlaceholder\s*/>;?\s*\}",
        re.MULTILINE | re.DOTALL
    )
    content = early_return_pattern.sub("", content)
    
    # 3. Add the safe variables right before the return (ClientModeBoundary)
    safe_vars_code = """
  const isOffline = error || !data;
  const m = isOffline ? { power_kw: '####', voltage: '####', current: '####', pf: '####', freq: '####', energy_kwh: '####', cost_inr: '####' } : data!.metrics;
  const q = isOffline ? { status: 'OFFLINE', alerts: ['Hardware Disconnected'] } : data!.quality;
  const tw = isOffline ? { nodes: [ {id:"GRID", name:"Utility Grid", voltage:"####", freq:"####"}, {id:"MAIN_METER", name:"L&T WL4400", power_kw:"####", current_a:"####", pf:"####"}, {id:"FACTORY_LOAD", name:"Aggregated Factory Load", power_kw:"####"} ] } : data!.twin;
  const cp = isOffline ? [] : data!.copilot;
"""

    if "return (" in content:
        # replace the first 'return (' inside the main function body 
        # But wait, chartOptions might use `data.metrics`. 
        # Let's replace 'data.metrics' -> 'm', 'data.quality' -> 'q', 'data.twin' -> 'tw', 'data.copilot' -> 'cp' 
        # inside the JSX and chart options.
        
        # It's safer to just inject the safe vars before chartOptions if it exists, otherwise before return
        if "const chartOptions" in content:
            content = content.replace("const chartOptions", safe_vars_code + "\n  const chartOptions")
        else:
            content = content.replace("return (", safe_vars_code + "\n  return (", 1)
            
        content = content.replace("data.metrics", "m")
        content = content.replace("data.quality", "q")
        content = content.replace("data.twin", "tw")
        content = content.replace("data.copilot", "cp")
        content = content.replace("data!", "data") # fix any weird typescript non-nulls if they existed

        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Patched {file_path}")
    else:
        print(f"Failed to patch {file_path}")

