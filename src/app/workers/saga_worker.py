from arq import cron
from arq.connections import RedisSettings, create_pool
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from enums.saga_enums import SagaStatus
from src.models.exchanges import Exchange
from src.services.exchange_service import ExchangeService
from src.db.db import new_session
from src.schemas.exchange_owners_schemas import ExchangeOwnerSchema
from src.schemas.exchange_schemas import ExchangeCreateSchema
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


async def run_create_exchange_saga(ctx, exchange_dict: dict, owner_dict: dict):
    owner_data = ExchangeOwnerSchema(**owner_dict)
    exchange_data = ExchangeCreateSchema(**exchange_dict, owner=owner_data)

    async with new_session() as session:
        orchestrator = ExchangeService(
            session=session,
            redis=ctx['redis_client'],
            market_data_client=ctx['market_data_service_client']
        )

        result = await orchestrator.create_exchange_with_saga_service(exchange_data=exchange_data)

        if result:
            return result.model_dump(mode='json')
        else:
            return None


async def recover_stuck_sagas(ctx):
    arq_redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    exchange_key = ''
    async with new_session() as session:
        query = (
            select(Exchange)
            .where(Exchange.status.in_([SagaStatus.FAILED, SagaStatus.PENDING]))
            .options(selectinload(Exchange.owner))
        )
        result = await session.execute(query)
        stuck_exchanges = result.scalars().all()

        for exchange in stuck_exchanges:
            exchange_schema = ExchangeCreateSchema.model_validate(exchange)
            exchange_dict = exchange_schema.model_dump(exclude='owner')
            owner_dict = exchange_schema.owner.model_dump()

            await arq_redis.enqueue_job(
                'run_create_exchange_saga',
                exchange_dict,
                owner_dict,
                exchange_key
            )

        await arq_redis.close()


class WorkerSettings:
    functions = [run_create_exchange_saga]
    on_startup = startup_worker
    on_shutdown = shutdown_worker
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 5

    cron_jobs = [
        cron('recover_stuck_sagas', minute=set(range(0, 60, 5)))
    ]