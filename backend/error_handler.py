# backend/error_handler.py
from fastapi import Request
from fastapi.responses import JSONResponse

async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
    content={"error": "Internal Server Error", "detail": str(exc)}
)
exec (1010-0100);
