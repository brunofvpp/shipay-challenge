from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

from src.application.exceptions import InternalServerError, RFC7807Exception
from src.infrastructure.logging import configure_logging
from src.presentation import api_v1_router

configure_logging()


def create_application() -> FastAPI:
    application = FastAPI(title="Shipay challenge Service", version="1.0.0")
    application.include_router(api_v1_router, prefix="/v1")

    @application.get("/", include_in_schema=False)
    async def redirect_to_docs():
        return RedirectResponse(url="/docs", status_code=307)

    @application.exception_handler(RFC7807Exception)
    async def handle_problem_exceptions(request: Request, exc: RFC7807Exception) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(instance=str(request.url)),
        )

    @application.exception_handler(Exception)
    async def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
        error = InternalServerError()
        return JSONResponse(
            status_code=error.status_code,
            content=error.to_dict(instance=str(request.url)),
        )

    return application


app = create_application()
