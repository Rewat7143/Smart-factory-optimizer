with open('backend/api/routes.py', 'r') as f:
    content = f.read()

import_statement = "from ml.maintenance import maintenance_engine\nfrom ml.copilot import copilot_engine\n\nrouter = APIRouter()"

content = content.replace("router = APIRouter()", import_statement)

with open('backend/api/routes.py', 'w') as f:
    f.write(content)
