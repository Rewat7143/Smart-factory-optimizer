with open('frontend/components/SidebarNav.tsx', 'r') as f:
    content = f.read()

# Replace Sidebar colors
content = content.replace('bg-white border-r border-slate-200 hidden md:flex flex-col', 'bg-slate-50 border-r border-slate-200 hidden md:flex flex-col shadow-inner')
# In case the sidebar was originally bg-slate-900 (now bg-white from the reversal)
content = content.replace('bg-white border-r border-slate-100 hidden md:flex flex-col', 'bg-slate-50 border-r border-slate-200 hidden md:flex flex-col')
content = content.replace('bg-white border-r border-slate-800', 'bg-slate-50 border-r border-slate-200')

# Update the Logo
content = content.replace('text-slate-900 tracking-tighter uppercase', 'text-slate-800 tracking-tighter uppercase')
content = content.replace('text-blue-500', 'text-teal-600')

# Update Links
content = content.replace('bg-blue-600 text-slate-900', 'bg-teal-700 text-white shadow-sm')
content = content.replace('text-slate-700 hover:bg-slate-50 hover:text-slate-900', 'text-slate-600 hover:bg-slate-200 hover:text-slate-900')

# Header borders inside sidebar
content = content.replace('border-slate-800', 'border-slate-200')
content = content.replace('text-slate-400', 'text-slate-500')

with open('frontend/components/SidebarNav.tsx', 'w') as f:
    f.write(content)
