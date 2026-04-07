from arq import cron
from arq.connections import RedisSettings
from redis.asyncio import Redis
from app.dependencies import get_exch_service
from src.db.db import new_session
from src.app.config import settings
from src.client.market_data_client import MarketDataClient


async def startup_worker(ctx):
    ctx['redis_client'] = Redis.from_url(settings.redis_url, decode_responses=True)
    ctx['market_data_service_client'] = MarketDataClient()


async def shutdown_worker(ctx):
    market_client = ctx.get('market_data_service_client')
    if market_client:
        await ctx['market_data_service_client'].client.aclose()

    redis_client = ctx.get('redis_client')
    if redis_client:
        await ctx['redis_client'].close()


async def cron_pending_batch(ctx):
    async with new_session() as session:
        exchange_service = get_exch_service(session=session, redis=ctx['redis_client'])
        await exchange_service.pending_batch_service()


async def cron_failed_batch(ctx):
    async with new_session() as session:
        exchange_service = get_exch_service(session=session, redis=ctx['redis_client'])
        await exchange_service.failed_batch_service()


async def cron_active_batch(ctx):
    async with new_session() as session:
        exchange_service = get_exch_service(session=session, redis=ctx['redis_client'])
        await exchange_service.active_batch_service()


class WorkerSettings:
    on_startup = startup_worker
    on_shutdown = shutdown_worker
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 5

    cron_jobs = [
        cron('cron_pending_batch', minute=set(range(0, 60, 1))),
        cron('cron_failed_batch', minute=set(range(0, 60, 5))),
        cron('cron_active_batch', minute=set(range(0, 60, 10)))
    ]