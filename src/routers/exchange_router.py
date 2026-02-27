from uuid import UUID
from fastapi import APIRouter, Depends, status
from src.services.schemas.exchange_owners_schemas import ExchangeOwnerUpdateSchema
from src.services.schemas.exchange_schemas import ExchangeSchema, ExchangeUpdateSchema
from src.app.dependencies import get_exch_service
from services.services.exchange_service import ExchangeService


router = APIRouter(tags=['Actions with the exchange'])

@router.post('/exchange', status_code=status.HTTP_201_CREATED)
async def create_exchange(exchange_data: ExchangeSchema, exchserv: ExchangeService = Depends(get_exch_service)):
    return await exchserv.create_exchange_service(exchange_data)


@router.get('/exchange', status_code=status.HTTP_200_OK)
async def get_exchanges(exchserv: ExchangeService = Depends(get_exch_service)):
    return await exchserv.get_exchanges_info_service()


@router.patch('/exchange/{exchange_id}', status_code=status.HTTP_200_OK)
async def update_exchange(exchange_id: UUID, update_data: ExchangeUpdateSchema, exchserv: ExchangeService = Depends(get_exch_service)):
    return await exchserv.update_exchange_info_service(exchange_id, update_data)


@router.patch('/exchange/{owner_id}', status_code=status.HTTP_200_OK)
async def update_owner(owner_id: UUID, update_data: ExchangeOwnerUpdateSchema, exchserv: ExchangeService = Depends(get_exch_service)):
    return await exchserv.update_owner_info_service(owner_id, update_data)


@router.delete('/exchange/{exchange_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_exchange_by_id(exchange_id: UUID, exchserv: ExchangeService = Depends(get_exch_service)):
    return await exchserv.delete_exchange_by_id(exchange_id)


@router.delete('/owner/{owner_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_owner_by_id(owner_id: UUID, exchserv: ExchangeService = Depends(get_exch_service)):
    return await exchserv.delete_owner_by_id(owner_id)