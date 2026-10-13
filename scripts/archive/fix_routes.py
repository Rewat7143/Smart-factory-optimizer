with open('backend/api/routes.py', 'r') as f:
    content = f.read()

content = content.replace("def get_copilot_insights():", "def get_copilot_insights(mode: str = 'SIMULATION'):")
content = content.replace("def get_predictive_maintenance():", "def get_predictive_maintenance(mode: str = 'SIMULATION'):")
content = content.replace("@router.get(\"/maintenance/status\")\ndef get_predictive_maintenance(mode: str = 'SIMULATION'):", "@router.get(\"/maintenance/status\")\ndef get_predictive_maintenance(mode: str = 'SIMULATION'):") # wait the name in the original file was get_predictive_maintenance ? No, it was get_predictive_maintenance for /maintenance/status

# Let's just blindly replace:
content = content.replace("def get_assets():", "def get_assets(mode: str = 'SIMULATION'):")
# Wait get_assets doesn't use _get_factory_state, it uses factory.assets directly.

with open('backend/api/routes.py', 'w') as f:
    f.write(content)
