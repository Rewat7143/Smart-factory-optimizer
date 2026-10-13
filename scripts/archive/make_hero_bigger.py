with open('frontend/components/CommandCenter.tsx', 'r') as f:
    content = f.read()

# Make the hero graph taller: 350px -> 500px
content = content.replace("h-[350px]", "h-[500px]")

# Make title huge
content = content.replace("text-6xl font-black", "text-7xl font-black tracking-tighter")

with open('frontend/components/CommandCenter.tsx', 'w') as f:
    f.write(content)
