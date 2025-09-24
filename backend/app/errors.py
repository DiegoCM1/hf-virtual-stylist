# errors.py
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

def add_error_handlers(app):
    @app.exception_handler(StarletteHTTPException)
    async def http_exc(_, exc):
        return JSONResponse({"error": {"code": exc.status_code, "message": exc.detail}}, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exc(_, exc):
        return JSONResponse({"error": {"code": 422, "message": "Validation error", "details": exc.errors()}}, status_code=422)

    @app.exception_handler(Exception)
    async def unhandled(_, exc):
        return JSONResponse({"error": {"code": 500, "message": "Internal server error"}}, status_code=500)
