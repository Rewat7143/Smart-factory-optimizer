import re

file_path = 'backend/api/routes.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
@router.api_route("/optimize", methods=["GET", "POST"])
def run_optimization(mode: str = "SIMULATION"):
"""

pattern = r'@router\.post\("/optimize"\)\ndef run_optimization\(mode: str = "SIMULATION"\):'
content = re.sub(pattern, replacement, content)

with open(file_path, 'w') as f:
    f.write(content)
