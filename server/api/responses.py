def api_response(data=None, message: str = "OK", status: int = 200):
    return {"status": status, "message": message, "data": data}
