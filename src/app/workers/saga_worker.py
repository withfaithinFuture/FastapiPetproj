import logging
from arq import cron
from arq.connections import RedisSettings
from redis.asyncio import Redis
from src.enums.saga_enums import SagaStatus
from src.app.dependencies import get_exch_service
from src.db.db import new_session
from src.app.config import settings
from src.client.market_data_client import MarketDataClient


class ExchangeSagaWorker:

    async def startup_worker(ctx: dict):
        ctx['redis_client'] = Redis.from_url(settings.redis_url, decode_responses=True)
        ctx['market_data_service_client'] = MarketDataClient()


    async def shutdown_worker(ctx: dict):
        market_client = ctx.get('market_data_service_client')
        if market_client:
            await ctx['market_data_service_client'].client.aclose()

        redis_client = ctx.get('redis_client')
        if redis_client:
            await ctx['redis_client'].close()


    async def process_exchange_by_status(ctx, status: SagaStatus, batch_size: int = 5):
        async with new_session() as session:
            exchange_service = get_exch_service(session=session, redis=ctx['redis_client'])
            exchanges = await exchange_service.exch_rep.get_batch_exchanges(status=status, batch_size=batch_size)
            if exchanges:
                for exchange in exchanges:
                    await exchange_service.create_exchange_with_saga_service(exchange)


    async def cron_pending_batch(ctx):
        await ExchangeSagaWorker.process_exchange_by_status(ctx=ctx, status=SagaStatus.PENDING)


    async def cron_failed_batch(ctx):
        await ExchangeSagaWorker.process_exchange_by_status(ctx=ctx, status=SagaStatus.FAILED)


    async def cron_active_batch(ctx):
        await ExchangeSagaWorker.process_exchange_by_status(ctx=ctx, status=SagaStatus.ACTIVE)


class WorkerSettings:
    on_startup = ExchangeSagaWorker.startup_worker
    on_shutdown = ExchangeSagaWorker.shutdown_worker
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 5

    cron_jobs = [
        cron(ExchangeSagaWorker.cron_pending_batch, minute=set(range(0, 60, 1))),
        cron(ExchangeSagaWorker.cron_failed_batch, minute=set(range(0, 60, 3))),
        cron(ExchangeSagaWorker.cron_active_batch, minute=set(range(0, 60, 5)))
    ]