import re

file_path = 'backend/main.py'
with open(file_path, 'r') as f:
    content = f.read()

# Add import
import_line = "from ml.online_learner import continuous_learning_loop\nimport asyncio\n"
content = content.replace('from api.google_sheets import gsheets_db\n', import_line + 'from api.google_sheets import gsheets_db\n')

# Add to startup_event
startup_replacement = """def startup_event():
    gsheets_db.connect()
    simulation_controller.start()
    asyncio.create_task(continuous_learning_loop())"""

content = content.replace("""def startup_event():
    gsheets_db.connect()
    simulation_controller.start()""", startup_replacement)

with open(file_path, 'w') as f:
    f.write(content)
