from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.services.club_service import ClubService
from src.services.services.exchange_service import ExchangeService
from src.services.services.second_client_service import SecondClientService
from src.services.services.shares_service import SharesService
from src.services.db.db import get_session


redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)
async def get_redis():
    yield redis_client


def get_club_service(session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis)) -> ClubService:
    return ClubService(session, redis)


def get_exch_service(session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis)) -> ExchangeService:
    second_service = SecondClientService()
    return ExchangeService(session, redis, second_service, 'exchanges_list')


def get_shares_service(session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis)) -> SharesService:
    return SharesService(session, redis)
