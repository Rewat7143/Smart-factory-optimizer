import re

file_path = 'backend/ml/copilot.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """
        # 3. Contextual operational insights
        total_power = factory_state.get('current_demand_kw', 0)
        from ml.opportunities import opportunity_engine
        
        # Check actual verifiable opportunities
        mode = factory_state.get('live_status', 'SIMULATION')
        ops = opportunity_engine.get_opportunities(mode)
        
        if ops:
            total_savings_inr = sum(o.get('cost_opportunity_inr', 0) for o in ops)
            evidence = [o.get('category') for o in ops]
            insights.append({
                "type": "OPERATIONAL_INSIGHT",
                "title": "Energy Efficiency Analysis",
                "content": f"Current factory demand is {total_power:.1f} kW. Based on verifiable evidence ({', '.join(evidence)}), executing pending optimization recommendations could avoid ₹{total_savings_inr:.0f} in unnecessary energy and peak penalties today.",
                "urgency": "LOW"
            })
        else:
            insights.append({
                "type": "OPERATIONAL_INSIGHT",
                "title": "Energy Efficiency Analysis",
                "content": f"Current factory demand is {total_power:.1f} kW. No immediate energy waste or peak penalty risks detected by the anomaly engine at this time.",
                "urgency": "LOW"
            })
"""

pattern = r'\s*# 3\. Contextual operational insights.*?urgency": "LOW"\s*\}\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
