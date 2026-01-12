from uuid import UUID
from fastapi import APIRouter, Depends
from src.services.schemas.exchange_schemas import ExchangeSchema, ExchangeUpdateSchema, \
    ExchangeOwnerUpdateSchema
from src.services.db.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.exchange_service import ExchangeService as ExchServ

router = APIRouter()

@router.post('/Биржа/Добавление биржи', tags=['Действия с биржами'])
async def add_exchange(exchange_data: ExchangeSchema, db_session: AsyncSession = Depends(get_session)):
    new_exchange = await ExchServ.add_exchange_service(exchange_data, db_session)
    return {'Exchange': new_exchange, 'HTTP status': 201}


@router.get('/Биржа/Получение бирж', tags=['Действия с биржами'])
async def get_exchanges(db_session: AsyncSession = Depends(get_session)):
    exchanges = await ExchServ.get_exchanges_info_service(db_session)
    return {"Exchanges": exchanges, 'HTTP status': 200}


@router.patch('/Биржа/Обновление биржи', tags=['Действия с биржами'])
async def update_exchange(exchange_id: UUID, update_data: ExchangeUpdateSchema, db_session: AsyncSession = Depends(get_session)):
    updated_exchange = await ExchServ.update_exchange_info_service(exchange_id, update_data, db_session)
    return {'New exchange info': updated_exchange, 'HTTP status': 200}


@router.patch('/Биржа/Обновление создателя биржи', tags=['Действия с биржами'])
async def update_owner(owner_id: UUID, update_data: ExchangeOwnerUpdateSchema, db_session: AsyncSession = Depends(get_session)):
    updated_owner = await ExchServ.update_owner_info_service(owner_id, update_data, db_session)
    return {'New owner info': updated_owner, 'HTTP status': 200}


@router.post('/Биржа/Удаление биржи с создателем', tags=['Действия с биржами'])
async def delete_exchange(delete_id: UUID, db_session: AsyncSession = Depends(get_session)):
    deleted_object = await ExchServ.delete_exchange_info_service(delete_id, db_session)
    return {'Deleted object': deleted_object, 'HTTP status': 200}
