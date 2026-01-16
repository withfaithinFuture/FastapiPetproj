from uuid import UUID
from fastapi import APIRouter, Depends
from src.services.schemas.exchange_schemas import ExchangeSchema, ExchangeUpdateSchema, \
    ExchangeOwnerUpdateSchema
from src.services.db.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.exchange_service import ExchangeService


router = APIRouter()

def get_exch_service(session: AsyncSession = Depends(get_session)):
    return ExchangeService(session)


@router.post('/Exchange/Add', tags=['Actions with the exchange'])
async def add_exchange(exchange_data: ExchangeSchema, exchserv: ExchangeService = Depends(get_exch_service)):
    return await exchserv.add_exchange_service(exchange_data)


@router.get('/Exchange/Get', tags=['Actions with the exchange'])
async def get_exchanges(exchserv: ExchangeService = Depends(get_exch_service)):
    return await exchserv.get_exchanges_info_service()


@router.patch('/Exchange/UpdateExchange', tags=['Actions with the exchange'])
async def update_exchange(exchange_id: UUID, update_data: ExchangeUpdateSchema, exchserv: ExchangeService = Depends(get_exch_service)):
    return await exchserv.update_exchange_info_service(exchange_id, update_data)


@router.patch('/Exchange/UpdateOwner', tags=['Actions with the exchange'])
async def update_owner(owner_id: UUID, update_data: ExchangeOwnerUpdateSchema, exchserv: ExchangeService = Depends(get_exch_service)):
    return await exchserv.update_owner_info_service(owner_id, update_data)


@router.post('/Exchange/Delete', tags=['Actions with the exchange'])
async def delete_exchange(delete_id: UUID, exchserv: ExchangeService = Depends(get_exch_service)):
    return await exchserv.delete_exchange_info_service(delete_id)
