import re

with open('frontend/app/layout.tsx', 'r') as f:
    content = f.read()

new_nav = """            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 mt-4 px-3">Operations</div>
            {[
              { name: 'Command Center', href: '/' },
              { name: 'Live Factory', href: '/live-factory' },
              { name: 'Digital Twin', href: '/digital-twin' },
              { name: 'Event Recorder', href: '/event-recorder' },
            ].map((item) => (
              <Link key={item.name} href={item.href} className="block px-3 py-2 rounded-md text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900">
                {item.name}
              </Link>
            ))}

            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 mt-6 px-3">Intelligence</div>
            {[
              { name: 'Energy Intelligence', href: '/energy' },
              { name: 'AI Center', href: '/forecast' },
              { name: 'Anomalies', href: '/opportunities' },
              { name: 'Optimization Lab', href: '/optimization-lab' },
              { name: 'What-If Simulator', href: '/what-if' },
              { name: 'Asset Intelligence', href: '/assets' },
            ].map((item) => (
              <Link key={item.name} href={item.href} className="block px-3 py-2 rounded-md text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900">
                {item.name}
              </Link>
            ))}

            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 mt-6 px-3">Enterprise</div>
            {[
              { name: 'Industry Test Workflow', href: '/industry-test' },
              { name: 'Energy Economics', href: '/business-impact' },
              { name: 'Fleet', href: '/fleet' },
              { name: 'System Hardware', href: '/hardware' }
            ].map((item) => (
              <Link key={item.name} href={item.href} className="block px-3 py-2 rounded-md text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900">
                {item.name}
              </Link>
            ))}"""

content = re.sub(r'<div className="text-\[10px\] font-bold text-slate-400 uppercase tracking-wider mb-2 mt-4 px-3">Operations</div>.*?</nav>', new_nav + "\n          </nav>", content, flags=re.DOTALL)

with open('frontend/app/layout.tsx', 'w') as f:
    f.write(content)
