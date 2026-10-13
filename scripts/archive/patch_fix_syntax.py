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
    
content = content.replace(pattern, replacement)

# wait, I need to make sure `days` and `daily_cost` variables don't cause NameError
# Let me just check if the pattern matched. If not, regex it.

with open(file_path, 'w') as f:
    f.write(content)
