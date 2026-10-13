with open('frontend/components/CommandCenter.tsx', 'r') as f:
    content = f.read()

# Make the hero number massive again
old_str = '''<div className="text-xl lg:text-2xl font-bold tracking-tight mb-6">{isOffline ? '₹ ####' : '₹ 18,460'} <span className="text-2xl text-teal-300">SAVED</span></div>'''
new_str = '''<div className="text-7xl lg:text-9xl font-black tracking-tighter mb-8 mt-4">{isOffline ? '₹ ####' : '₹ 18,460'} <span className="text-4xl lg:text-5xl text-teal-300 font-bold ml-2">SAVED</span></div>'''

content = content.replace(old_str, new_str)

with open('frontend/components/CommandCenter.tsx', 'w') as f:
    f.write(content)
