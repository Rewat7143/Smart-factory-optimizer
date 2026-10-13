with open('frontend/components/SidebarNav.tsx', 'r') as f:
    content = f.read()

# Replace the links logic to always use the 11 links
replacement = """
  const links = [
    { name: 'Command Center', href: '/' },
    { name: 'Factory', href: '/live-factory' },
    { name: 'Digital Twin', href: '/digital-twin' },
    { name: 'Intelligence', href: '/forecast' },
    { name: 'Optimization', href: '/optimization-lab' },
    { name: 'Counterfactual', href: '/counterfactual' },
    { name: 'Predictive Maint.', href: '/predictive-maintenance' },
    { name: 'AI Copilot', href: '/industrial-copilot' },
    { name: 'Energy Economics', href: '/energy-economics' },
    { name: 'Scale Simulator', href: '/scale-simulator' },
    { name: 'Reports', href: '/business-impact' },
  ]
"""
import re
content = re.sub(r"const simLinks = \[.*?\]\s*const liveLinks = \[.*?\]\s*const links = .*?\n", replacement, content, flags=re.DOTALL)

with open('frontend/components/SidebarNav.tsx', 'w') as f:
    f.write(content)
