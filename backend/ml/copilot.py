import datetime

class IndustrialCopilot:
    def generate_insights(self, factory_state: dict, maintenance_data: list = None, alerts: list = None, optimization_result: dict = None, economics_data: dict = None):
        """
        Combines human knowledge with artificial intelligence to streamline workflows.
        Simulates an LLM evaluating the entire factory context.
        """
        insights = []
        alerts = alerts or []
        maintenance_data = maintenance_data or []
        
        # 1. Real-time problem solving
        if alerts:
            insights.append({
                "type": "PROBLEM_SOLVING",
                "title": "Alert Triage Assistance",
                "content": f"I detected {len(alerts)} active alerts. Based on historical resolution patterns, {alerts[0].get('asset_id', 'the affected machine')} typically requires a power-cycle and thermal inspection. Would you like me to generate a maintenance ticket?",
                "urgency": "HIGH"
            })
            
        # 2. Intelligent process guidance (Predictive Maintenance)
        if maintenance_data:
            critical_assets = [a for a in maintenance_data if a.get('status') == 'CRITICAL']
            if critical_assets:
                insights.append({
                    "type": "PROCESS_GUIDANCE",
                    "title": "Maintenance Optimization",
                    "content": f"Asset {critical_assets[0].get('name', 'Unknown')} is showing a critical health score ({critical_assets[0].get('health_score', 0)}%). I recommend re-routing production to flexible lines to minimize downtime risk while the maintenance team intervenes.",
                    "urgency": "MEDIUM"
                })
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

        
        # New Insight Type: WHY_EXPLANATION
        if optimization_result:
            actions = optimization_result.get('actions', [])
            peak_before = optimization_result.get('before_peak', total_power)
            peak_after = optimization_result.get('after_peak', total_power)
            saved = peak_before - peak_after
            if actions:
                action_desc = ", ".join([a.get('action', 'adjustment') + " on " + a.get('asset_id', 'asset') for a in actions[:2]])
                insights.append({
                    "type": "WHY_EXPLANATION",
                    "title": "Optimizer Decision Reasoning",
                    "content": f"To prevent breaching the safe operating target, the AI recommended {action_desc}. This reduces predicted peak demand from {peak_before:.1f} kW to {peak_after:.1f} kW (saving {saved:.1f} kW) without impacting the production target.",
                    "urgency": "MEDIUM"
                })
        
        # 4. Knowledge capture and sharing
        insights.append({
            "type": "KNOWLEDGE_SHARE",
            "title": "Shift Handover Summary",
            "content": "Shift operations have been stable. I have captured the load profiles and optimization actions applied by the AI during this shift. They have been logged to the operational knowledge base for future training.",
            "urgency": "LOW"
        })
        
        return insights

copilot_engine = IndustrialCopilot()
