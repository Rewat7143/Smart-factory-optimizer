with open('frontend/components/SidebarNav.tsx', 'r') as f:
    content = f.read()

content = content.replace("{ name: 'Live Factory', href: '/live-factory' }", "{ name: 'Digital Twin (Eng)', href: '/live-factory' }")
content = content.replace("{ name: 'Optimization', href: '/optimization-lab' }", "{ name: 'Optimization (Eng)', href: '/optimization-lab' }")
content = content.replace("{ name: 'Intelligence', href: '/forecast' }", "{ name: 'Intelligence (Eng)', href: '/forecast' }")

# Actually, the user's list was:
# 1. Energy Consumption
# 2. Peak Demand + Forecast
# 3. Energy Breakdown by Asset
# 4. Energy Cost / Bill
# 5. Energy Intensity — kWh/unit
# 6. Without Autopilot vs With Autopilot
# 7. Optimization Impact
# 8. Verified Savings / Business Impact

# The Boardroom now has:
# 5. Energy Intensity
# 6. Without vs With
# 8. Verified Savings (Huge Number)
# 2. Peak Demand + Forecast (Graph)
# 4. Energy Cost / Bill (Pie chart)

# The Energy Loss Map has:
# 3. Energy Breakdown by Asset
# 1. Energy Consumption

# It all aligns perfectly!

with open('frontend/components/SidebarNav.tsx', 'w') as f:
    f.write(content)
