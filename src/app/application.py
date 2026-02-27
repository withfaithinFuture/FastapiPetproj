from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from starlette.middleware.cors import CORSMiddleware
from src.routers.shares_router import router as shares_router
from src.routers.exchange_router import router as exchange_router
from src.routers.clubs_router import router as clubs_router
from src.routers.healthcheck_router import router as healthcheck_router



def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        docs_url='/docs',
        openapi_url='/openapi.json',
        default_response_class=UJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.include_router(clubs_router)
    app.include_router(exchange_router)
    app.include_router(shares_router)
    app.include_router(healthcheck_router)


    return app