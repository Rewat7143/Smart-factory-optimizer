import re

file_path = 'frontend/app/verified-ledger/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

# I want to add `const isLive = typeof window !== 'undefined' && localStorage.getItem('FEA_MODE') === 'LIVE';`
# Then conditionally render the numbers.

content = content.replace("const isOffline = data.live_status === 'OFFLINE';", 
"""const isOffline = data.live_status === 'OFFLINE';
  const isLive = typeof window !== 'undefined' ? localStorage.getItem('FEA_MODE') === 'LIVE' : false;""")

# Update the top 4 boxes
content = content.replace("{isOffline ? '₹####' : '₹18,460'}", "{isOffline ? '₹####' : isLive ? 'CALCULATING...' : '₹18,460'}")
content = content.replace("{isOffline ? '₹####' : '₹4.82L'}", "{isOffline ? '₹####' : isLive ? 'CALCULATING...' : '₹4.82L'}")
content = content.replace("{isOffline ? '₹####' : '₹41.7L'}", "{isOffline ? '₹####' : isLive ? 'CALCULATING...' : '₹41.7L'}")
content = content.replace("{isOffline ? '₹####' : '₹1.14Cr'}", "{isOffline ? '₹####' : isLive ? 'CALCULATING...' : '₹1.14Cr'}")

# Update the table mapping: if isLive, don't show the hardcoded history array, show a single row saying "Awaiting verified optimization cycle on live meter."
table_render = """               {(!isOffline && !isLive) && history.map((h, i) => ("""
content = content.replace("""               {!isOffline && history.map((h, i) => (""", table_render)

table_wait = """               {(isOffline || isLive) && (
                  <tr><td colSpan={7} className="p-8 text-center text-sm font-bold text-slate-500">{isLive ? "Awaiting optimization cycle on live meter..." : "Waiting for telemetry to verify outcomes..."}</td></tr>
               )}"""
content = content.replace("""               {isOffline && (
                  <tr><td colSpan={7} className="p-8 text-center text-sm font-bold text-slate-500">Waiting for telemetry to verify outcomes...</td></tr>
               )}""", table_wait)

with open(file_path, 'w') as f:
    f.write(content)
