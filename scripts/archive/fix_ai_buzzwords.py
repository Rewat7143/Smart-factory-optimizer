import os
import re

replacements = {
    "AI-Driven Peak Prediction & Anomaly Detection": "Peak Prediction & Anomaly Detection",
    "Production-Constrained AI Scheduler": "Production-Constrained Optimizer",
    "AI scheduling boundaries determined": "Scheduling boundaries determined",
    "latest scheduled AI intervention": "latest scheduled intervention",
    "Predicted Peak (Without AI)": "Predicted Peak (Without Autopilot)",
    "Optimized Peak (With AI)": "Optimized Peak (With Autopilot)",
    "AI Decisions": "Optimization Actions",
    "AI Copilot": "Industrial Copilot",
    "Live AI Copilot": "Live Copilot",
    "AI offline": "Copilot offline",
    "Before AI": "Before Autopilot",
    "After AI": "After Autopilot",
    "If You Follow AI": "With Optimization",
    "Apply AI Schedule": "Apply Schedule",
    "AI Engine Active": "Optimizer Active",
    "AI intelligence": "Intelligence",
    "Auditable record of AI optimization outcomes": "Auditable record of optimization outcomes"
}

directories = ['frontend/app', 'frontend/components']

for root, _, files in os.walk('frontend'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            
            original = content
            for old, new in replacements.items():
                content = content.replace(old, new)
            
            if content != original:
                with open(path, 'w') as f:
                    f.write(content)

