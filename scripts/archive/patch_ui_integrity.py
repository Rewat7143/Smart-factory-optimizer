import re

def patch():
    with open('frontend/components/CommandCenter.tsx', 'r') as f:
        content = f.read()

    # 1. Add state variable
    content = content.replace(
        "const [registry, setRegistry] = useState<any>(null)",
        "const [registry, setRegistry] = useState<any>(null)\n  const [integrity, setIntegrity] = useState<any>(null)"
    )
    
    # 2. Add fetch call
    fetch_target = "fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/forecast/registry`)"
    if fetch_target in content:
        content = content.replace(
            fetch_target,
            fetch_target + ",\n        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/integrity/status`)"
        )
    
    # 3. Add JSON parse
    json_target = "if (regRes.ok) setRegistry(await regRes.json())"
    if json_target in content:
        content = content.replace(
            json_target,
            json_target + "\n      if (integrityRes && integrityRes.ok) setIntegrity(await integrityRes.json())"
        )
        
    # Wait, the Promise.all array destructuring also needs update:
    destruct_target = "const [stateRes, histRes, optRes, regRes]"
    if destruct_target in content:
        content = content.replace(
            destruct_target,
            "const [stateRes, histRes, optRes, regRes, integrityRes]"
        )

    # 4. Add the UI section at the end, just before the closing </div> of the main wrapper
    # Let's find the end of the return statement
    ui_block = """
      {/* 6. DATA INTEGRITY MONITOR */}
      {integrity && (
         <div className="pt-6 border-t border-slate-200 mt-6">
            <h3 className="text-xs font-black tracking-widest uppercase text-slate-800 mb-6 pb-2 border-b border-slate-100 flex items-center gap-2">
               <svg className="w-4 h-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
               Energy Data Integrity Monitor
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
               {integrity.checks && integrity.checks.map((check: any, idx: number) => (
                  <div key={idx} className={`p-4 rounded-xl border ${check.status === 'WARNING' ? 'border-amber-300 bg-amber-50' : 'border-slate-200 bg-white'}`}>
                     <div className="flex justify-between items-center mb-3">
                        <div className="text-[10px] uppercase font-bold text-slate-500 tracking-widest">{check.name}</div>
                        {check.status === 'WARNING' ? (
                           <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                        ) : (
                           <div className="w-2 h-2 rounded-full bg-green-500"></div>
                        )}
                     </div>
                     <div className="flex justify-between items-end mb-2">
                        <div>
                           <div className="text-[9px] text-slate-400 uppercase tracking-widest mb-1">PLC Edge</div>
                           <div className="font-mono text-sm font-bold text-slate-700">{check.reported_kw.toFixed(1)} kW</div>
                        </div>
                        <div className="text-right">
                           <div className="text-[9px] text-slate-400 uppercase tracking-widest mb-1">L&T Meter</div>
                           <div className="font-mono text-sm font-bold text-slate-700">{check.measured_kw.toFixed(1)} kW</div>
                        </div>
                     </div>
                     {check.status === 'WARNING' && (
                        <div className="mt-3 pt-3 border-t border-amber-200 text-[9px] text-amber-700 font-bold uppercase tracking-widest flex items-center justify-between">
                           <span>Deviation</span>
                           <span>{check.deviation_percent.toFixed(1)}%</span>
                        </div>
                     )}
                  </div>
               ))}
            </div>
         </div>
      )}
    </div>
  )
}

function StatusCard"""
    
    content = content.replace("    </div>\n  )\n}\n\nfunction StatusCard", ui_block)
    
    with open('frontend/components/CommandCenter.tsx', 'w') as f:
        f.write(content)
        
    print("Patched Integrity")

patch()
