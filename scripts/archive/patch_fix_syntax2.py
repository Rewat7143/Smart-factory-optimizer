import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

pattern = r'    return \{\n        "timeline": times,\n        "demand": demand,\n        "cost_breakdown": \[\], # Aggregate meter doesn\'t know breakdown\n        "live_status": "CONNECTED"\n    \},\n        "daily_cost": \{\n            "days": days,\n            "cost_inr": daily_cost\n        \}\n    \}'

replacement = """    return {
        "timeline": times,
        "demand": demand,
        "cost_breakdown": [],
        "live_status": "CONNECTED",
        "daily_cost": {
            "days": [],
            "cost_inr": []
        }
    }"""
    
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
