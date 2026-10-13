import random

class DataIntegrityMonitor:
    def check_integrity(self, factory_state: dict) -> dict:
        assets = factory_state.get('assets', [])
        checks = []
        status = 'HEALTHY'
        
        for a in assets:
            reported = a.get('operating_power_kw', 0)
            drift = random.uniform(0.9, 1.2)
            measured = reported * drift
            
            dev = abs(measured - reported) / reported * 100 if reported > 0 else 0
            
            astat = 'HEALTHY'
            if dev > 15:
                astat = 'INTEGRITY_WARNING'
                status = 'WARNING'
            
            checks.append({
                'asset_id': a.get('asset_id', 'UNKNOWN'),
                'name': a.get('name', 'Unknown'),
                'reported_kw': round(reported, 2),
                'measured_kw': round(measured, 2),
                'deviation_percent': round(dev, 2),
                'status': astat
            })
            
        return {
            'status': status,
            'checks': checks
        }

integrity_monitor = DataIntegrityMonitor()
