with open('frontend/app/forecast/page.tsx', 'r') as f:
    content = f.read()

import re
# The section starts with "{/* MODEL CENTER CONTENT */}" and ends at the closing brace of the page.
# Let's cleanly regex it out.
content = re.sub(r"\{\/\* MODEL CENTER CONTENT \*\/\}.*?</div>\n        \)\}\n", "", content, flags=re.DOTALL)

with open('frontend/app/forecast/page.tsx', 'w') as f:
    f.write(content)
