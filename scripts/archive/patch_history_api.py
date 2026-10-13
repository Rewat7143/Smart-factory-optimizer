with open('backend/api/telemetry.py', 'r') as f:
    content = f.read()

new_endpoint = """
@router.get("/telemetry/history_explorer")
def get_history_explorer(
    start_time: str,
    end_time: str,
    source: str = None,
    asset_id: str = None,
    limit: int = 5000,
    offset: int = 0
):
    from database.db import query_telemetry, count_telemetry
    
    records = query_telemetry(start_time, end_time, source, asset_id, limit, offset)
    total_count = count_telemetry(start_time, end_time, source, asset_id)
    
    return {
        "records": records,
        "total_count": total_count,
        "limit": limit,
        "offset": offset
    }

"""

if '/telemetry/history_explorer' not in content:
    content += new_endpoint
    with open('backend/api/telemetry.py', 'w') as f:
        f.write(content)
