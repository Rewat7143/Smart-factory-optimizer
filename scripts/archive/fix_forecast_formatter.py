with open('frontend/app/forecast/page.tsx', 'r') as f:
    content = f.read()

# Replace the fragile formatter with a robust one
old_formatter = "formatter: (val: string) => val.split('T')[1].substring(0,5)"
new_formatter = "formatter: (val: string) => val ? (val.includes('T') ? val.split('T')[1].substring(0,5) : String(val).substring(0,10)) : ''"

content = content.replace(old_formatter, new_formatter)

with open('frontend/app/forecast/page.tsx', 'w') as f:
    f.write(content)
