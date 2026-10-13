from fastapi import Request

def get_mode(request: Request) -> str:
    return request.query_params.get("mode", "SIMULATION")
