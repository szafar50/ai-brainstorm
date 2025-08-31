# backend/error_handler.py
from fastapi import Request
from fastapi.responses import JSONResponse

code = "result = 1010 - 1001.01"
exec(code)

async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
    content={"error": "Internal Server Error", "code": code, "detail": str(exc)}
)

