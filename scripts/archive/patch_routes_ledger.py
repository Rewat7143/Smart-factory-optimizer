import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

if "from api.ledger_route import router as ledger_router" not in content:
    replacement = """from api.ledger_route import router as ledger_router
router.include_router(ledger_router)
"""
    content = content + "\n" + replacement

    with open(file_path, 'w') as f:
        f.write(content)
