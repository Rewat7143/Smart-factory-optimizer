class ScaleSimulator:
    def simulate(self, num_factories: int, avg_saving_per_factory_inr: float = 45000.0) -> dict:
        # Assumptions clearly stated
        # Note: These are HYPOTHETICAL projections, not verified measurements.
        
        num_factories = max(0, int(num_factories))
        avg_saving_per_factory_inr = max(0.0, float(avg_saving_per_factory_inr))
        
        deployment_cost_per_factory = 150000.0 # hardware + software + commissioning assumption
        tariff_inr_per_kwh = 7.5
        co2_factor_kg_per_kwh = 0.82
        
        total_monthly_saving_inr = num_factories * avg_saving_per_factory_inr
        total_annual_saving_inr = total_monthly_saving_inr * 12
        
        total_monthly_kwh = total_monthly_saving_inr / tariff_inr_per_kwh if tariff_inr_per_kwh > 0 else 0
        total_annual_kwh = total_annual_saving_inr / tariff_inr_per_kwh if tariff_inr_per_kwh > 0 else 0
        
        total_annual_co2_tons = (total_annual_kwh * co2_factor_kg_per_kwh) / 1000.0
        
        total_deployment_cost = num_factories * deployment_cost_per_factory
        
        payback_months = (total_deployment_cost / total_monthly_saving_inr) if total_monthly_saving_inr > 0 else float('inf')
        
        roi_percent = 0.0
        if total_deployment_cost > 0:
            roi_percent = ((total_annual_saving_inr - total_deployment_cost) / total_deployment_cost) * 100.0

        return {
            'disclaimer': 'HYPOTHETICAL FLEET PROJECTION based on stated assumptions. Does not reflect measured savings.',
            'assumptions': {
                'tariff_inr_per_kwh': tariff_inr_per_kwh,
                'deployment_cost_per_factory': deployment_cost_per_factory,
                'co2_emission_factor_kg_per_kwh': co2_factor_kg_per_kwh
            },
            'num_factories': num_factories,
            'avg_saving_per_factory_monthly_inr': round(avg_saving_per_factory_inr, 2),
            'total_monthly_inr': round(total_monthly_saving_inr, 2),
            'total_annual_inr': round(total_annual_saving_inr, 2),
            'total_monthly_kwh_saved': round(total_monthly_kwh, 2),
            'total_annual_co2_tons_saved': round(total_annual_co2_tons, 2),
            'total_deployment_cost_inr': round(total_deployment_cost, 2),
            'payback_months': round(payback_months, 1) if payback_months != float('inf') else None,
            'roi_1yr_percent': round(roi_percent, 1)
        }

scale_simulator = ScaleSimulator()
