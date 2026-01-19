from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.services.club_service import ClubService
from services.services.exchange_service import ExchangeService
from services.services.shares_service import SharesService
from src.services.db.db import get_session


def get_club_service(session: AsyncSession = Depends(get_session)) -> ClubService:
    return ClubService(session)


def get_exch_service(session: AsyncSession = Depends(get_session)) -> ExchangeService:
    return ExchangeService(session)


def get_shares_service(session: AsyncSession = Depends(get_session)) -> SharesService:
    return SharesService(session)