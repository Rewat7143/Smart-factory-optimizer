import os

directories = ['frontend/app']

for root, _, files in os.walk('frontend/app'):
    for file in files:
        if file.endswith('.tsx'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            
            original = content
            content = content.replace("import { ClientModeBoundary } from '@/components/ClientModeBoundary'\n", "")
            content = content.replace("import { ClientModeBoundary } from '../components/ClientModeBoundary'\n", "")
            content = content.replace("<ClientModeBoundary>", "")
            content = content.replace("</ClientModeBoundary>", "")
            
            # Also remove fake tabs from forecast
            if 'forecast/page.tsx' in path:
                # Remove tabs div
                import re
                content = re.sub(r"\{\/\* TABS \*\/\}.*?</div>", "", content, flags=re.DOTALL)
                content = content.replace("{activeTab !== 'Model Center' && (", "")
                content = content.replace("<>", "")
                content = content.replace("</>", "")
                # Change {activeTab === 'Model Center' && registry && ( to {registry && (
                content = content.replace("{activeTab === 'Model Center' && registry && (", "{registry && (")
                content = content.replace("const [activeTab, setActiveTab] = useState('Overview');", "")
                
            if content != original:
                with open(path, 'w') as f:
                    f.write(content)
                    print(f"Stripped boundary from {path}")

