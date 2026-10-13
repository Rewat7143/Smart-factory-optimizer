with open('frontend/components/CommandCenter.tsx', 'r') as f:
    content = f.read()

import re

# We will replace {something.toFixed(1)} with {state.live_status === 'OFFLINE' ? '####' : something.toFixed(1)}
# This is tricky with regex. Let's do it manually for the top cards.

# In CommandCenter.tsx:
# <StatusCard title="Current Demand" value={`${currentDemand.toFixed(1)} kW`} color="blue" />
# We want: value={state.live_status === 'OFFLINE' ? '#### kW' : `${currentDemand.toFixed(1)} kW`}

content = content.replace('value={`${currentDemand.toFixed(1)} kW`}', 'value={state.live_status === \'OFFLINE\' ? \'#### kW\' : `${currentDemand.toFixed(1)} kW`}')
content = content.replace('value={`${forecast15m.toFixed(1)} kW`}', 'value={state.live_status === \'OFFLINE\' ? \'#### kW\' : `${forecast15m.toFixed(1)} kW`}')
content = content.replace('value={`${demandLimit.toFixed(1)} kW`}', 'value={state.live_status === \'OFFLINE\' ? \'#### kW\' : `${demandLimit.toFixed(1)} kW`}')
content = content.replace('value={`${headroom.toFixed(1)} kW`}', 'value={state.live_status === \'OFFLINE\' ? \'#### kW\' : `${headroom.toFixed(1)} kW`}')
content = content.replace('value={`${state.energy_today_kwh?.toFixed(1) || 0} kWh`}', 'value={state.live_status === \'OFFLINE\' ? \'#### kWh\' : `${state.energy_today_kwh?.toFixed(1) || 0} kWh`}')
content = content.replace('value={`₹${state.cost_today_inr?.toFixed(0) || 0}`}', 'value={state.live_status === \'OFFLINE\' ? \'₹####\' : `₹${state.cost_today_inr?.toFixed(0) || 0}`}')
content = content.replace('value={`${state.production_percent?.toFixed(0) || 100}%`}', 'value={state.live_status === \'OFFLINE\' ? \'####%\' : `${state.production_percent?.toFixed(0) || 100}%`}')

# Replace the "SYSTEM HEALTHY" or whatever with OFFLINE
content = content.replace('>SYSTEM HEALTHY<', '>{state.live_status === \'OFFLINE\' ? \'METER OFFLINE\' : \'SYSTEM HEALTHY\'}<')

with open('frontend/components/CommandCenter.tsx', 'w') as f:
    f.write(content)

