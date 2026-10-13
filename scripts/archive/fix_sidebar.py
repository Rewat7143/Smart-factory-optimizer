with open('frontend/components/SidebarNav.tsx', 'r') as f:
    content = f.read()

target = '<div className="text-sm font-bold text-slate-800 uppercase tracking-widest mb-2 px-2">Engineering / Config</div>'
replacement = target + '\n         <Link href="/telemetry" className={`block px-2 py-2 rounded text-sm font-bold hover:text-slate-800 ${pathname === "/telemetry" ? "text-slate-800" : "text-slate-500"}`}>Hardware Telemetry</Link>'

if 'href="/telemetry"' not in content:
    content = content.replace(target, replacement)
    with open('frontend/components/SidebarNav.tsx', 'w') as f:
        f.write(content)
