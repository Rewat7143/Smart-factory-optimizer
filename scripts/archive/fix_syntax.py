import re

file_path = 'frontend/app/optimization-lab/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

content = re.sub(r'<\/div>\s*:\s*\(', '</div>\n              ) : (', content)

with open(file_path, 'w') as f:
    f.write(content)
