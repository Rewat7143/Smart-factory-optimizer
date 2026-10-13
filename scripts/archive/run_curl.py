import subprocess
print(subprocess.check_output(['curl', '-X', 'POST', 'http://127.0.0.1:8000/api/optimize']).decode())
