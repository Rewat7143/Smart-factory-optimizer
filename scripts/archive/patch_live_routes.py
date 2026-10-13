import re
with open('backend/api/routes.py', 'r') as f:
    content = f.read()
if "from api.live_routes import router as live_router" not in content:
    content = content.replace("router = APIRouter()", "router = APIRouter()\nfrom api.live_routes import router as live_router\nrouter.include_router(live_router)")
    with open('backend/api/routes.py', 'w') as f:
        f.write(content)
