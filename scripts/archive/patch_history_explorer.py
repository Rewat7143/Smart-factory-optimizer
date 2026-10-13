import re

with open('frontend/app/history-explorer/page.tsx', 'r') as f:
    content = f.read()

content = content.replace("`http://localhost:8000/api/telemetry/history_explorer", "`${typeof window !== 'undefined' ? window.location.protocol + '//' + window.location.hostname + ':8000/api' : 'http://localhost:8000/api'}/telemetry/history_explorer")
content = content.replace("'http://localhost:8000/api/forecast/custom'", "`${typeof window !== 'undefined' ? window.location.protocol + '//' + window.location.hostname + ':8000/api' : 'http://localhost:8000/api'}/forecast/custom`")

with open('frontend/app/history-explorer/page.tsx', 'w') as f:
    f.write(content)
