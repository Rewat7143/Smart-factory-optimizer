with open('frontend/components/SidebarNav.tsx', 'r') as f:
    content = f.read()

# Add to Engineering / Config section
new_link = '''<div className="text-sm font-bold text-slate-800 uppercase tracking-widest mb-2 px-2">Engineering / Config</div>
         <Link href="/telemetry" className={`block px-2 py-2 rounded text-sm font-bold hover:text-slate-800 transition-colors ${pathname === '/telemetry' ? 'text-slate-800 bg-slate-200' : 'text-slate-500'}`}>Hardware Telemetry</Link>'''

content = content.replace('<div className="text-sm font-black text-slate-800 uppercase tracking-widest mb-2 px-2">Engineering / Config</div>', new_link)

with open('frontend/components/SidebarNav.tsx', 'w') as f:
    f.write(content)
