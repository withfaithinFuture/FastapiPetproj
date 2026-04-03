from arq import create_pool
from arq.connections import RedisSettings, ArqRedis
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.club_service import ClubService
from src.services.exchange_service import ExchangeService
from src.services.shares_service import SharesService
from src.client.market_data_client import MarketDataClient
from src.db.db import get_session, settings


redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
async def get_redis():
    yield redis_client


async def get_arq_pool():
    pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))

    yield pool

    await pool.close()


def get_club_service(session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis)) -> ClubService:
    return ClubService(session, redis)


def get_exch_service(session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis), arq_pool: ArqRedis = Depends(get_arq_pool)) -> ExchangeService:
    second_service = MarketDataClient()
    return ExchangeService(session, redis, second_service, arq_pool)


def get_shares_service(session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis)) -> SharesService:
    return SharesService(session, redis)
