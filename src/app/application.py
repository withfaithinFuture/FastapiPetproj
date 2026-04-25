import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.app.workers.outbox_worker import OutboxWorker
from src.app.config import settings
from src.db.redis_client import redis_client
from src.routers.shares_router import router as shares_router
from src.routers.exchange_router import router as exchange_router
from src.routers.clubs_router import router as clubs_router
from src.routers.healthcheck_router import router as healthcheck_router
from src.client.kafka_client import KafkaProducerClient


kafka_producer = KafkaProducerClient(servers=settings.KAFKA_URL)
outbox_worker = OutboxWorker(kafka_client=kafka_producer)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await kafka_producer.start()
    outbox_start_task = asyncio.create_task(outbox_worker.run(batch_size=30, interval_sec=3.0))

    yield

    outbox_start_task.cancel()
    await kafka_producer.stop()
    await redis_client.close()


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        docs_url='/docs',
        openapi_url='/openapi.json',
        lifespan=lifespan
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