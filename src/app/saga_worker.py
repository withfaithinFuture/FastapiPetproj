from arq.connections import RedisSettings
from redis.asyncio import Redis
from src.services.db.db import new_session
from src.services.repositories.exchanges_repo import ExchangesOwnersRepository
from src.services.services.exchange_orchestrator import ExchangeOrchestratorService
from src.services.schemas.exchange_owners_schemas import ExchangeOwnerSchema
from src.services.schemas.exchange_schemas import ExchangeCreateSchema
from src.app.config import Settings
from src.client.market_data_client import MarketDataClient


settings = Settings()

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


async def run_create_exchange_saga(ctx, exchange_dict: dict, owner_dict: dict, exchange_key: str):
    owner_data = ExchangeOwnerSchema(**owner_dict)
    exchange_data = ExchangeCreateSchema(**exchange_dict, owner=owner_data)

    async with new_session() as session:
        exchange_repo = ExchangesOwnersRepository(session=session)

        orchestrator = ExchangeOrchestratorService(
            exchange_repo=exchange_repo,
            market_data_client=ctx['market_data_service_client'],
            redis=ctx['redis_client']
        )

        result = await orchestrator.create_exchange_with_saga(exchange_data=exchange_data, exchange_key=exchange_key)

        if result:
            return result.model_dump(mode='json')
        else:
            return None


class WorkerSettings:
    functions = [run_create_exchange_saga]
    on_startup = startup_worker
    on_shutdown = shutdown_worker

    redis_settings = RedisSettings.from_dsn(settings.redis_url)

    max_jobs = 5