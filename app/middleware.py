from fastapi import Request, status
from fastapi.responses import JSONResponse
from traceback import print_exception

async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # Log the exception details
        print_exception(type(e), e, e.__traceback__)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred. Please try again later."},
        )