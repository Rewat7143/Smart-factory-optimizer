import json

with open('frontend/package.json', 'r') as f:
    pkg = json.load(f)

pkg['scripts']['build'] = 'next build --webpack'

with open('frontend/package.json', 'w') as f:
    json.dump(pkg, f, indent=2)
