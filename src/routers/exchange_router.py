from uuid import UUID
from fastapi import APIRouter, Depends, status

from src.services.core.exceptions import NotFoundByNameError, NotFoundError
from src.services.schemas.exchange_owners_schemas import ExchangeOwnerUpdateSchema
from src.services.schemas.exchange_schemas import ExchangeCreateSchema, ExchangeUpdateSchema
from src.app.dependencies import get_exch_service
from src.services.services.exchange_service import ExchangeService


router = APIRouter(tags=['Actions with the exchange'])

@router.post('/exchange', status_code=status.HTTP_201_CREATED)
async def create_exchange(exchange_data: ExchangeCreateSchema, exchserv: ExchangeService = Depends(get_exch_service)):
    return await exchserv.create_exchange_service(exchange_data)


@router.get('/exchange', status_code=status.HTTP_200_OK)
async def get_exchanges(exchserv: ExchangeService = Depends(get_exch_service)):
    return await exchserv.get_exchanges_info_service()


@router.get('/exchange/{exchange_name}', status_code=status.HTTP_200_OK)
async def get_exchange_by_name(exchange_name: str, exchserv: ExchangeService = Depends(get_exch_service)):
    exchange = await exchserv.get_exchange_by_name(exchange_name)
    if exchange is None:
        raise NotFoundByNameError(exchange_name, 'Exchange')

    return await exchserv.get_exchange_by_name(exchange_name)


@router.patch('/exchange/{exchange_id}', status_code=status.HTTP_200_OK)
async def update_exchange(exchange_id: UUID, update_data: ExchangeUpdateSchema, exchserv: ExchangeService = Depends(get_exch_service)):
    updated_exchange = await exchserv.update_exchange_info_service(exchange_id, update_data)
    if updated_exchange is None:
        raise NotFoundError(exchange_id, "exchange")

    return updated_exchange


@router.patch('/exchange/{owner_id}', status_code=status.HTTP_200_OK)
async def update_owner(owner_id: UUID, update_data: ExchangeOwnerUpdateSchema, exchserv: ExchangeService = Depends(get_exch_service)):
    updated_owner =  await exchserv.update_owner_info_service(owner_id, update_data)
    if updated_owner is None:
        raise NotFoundError(owner_id, "owner")

    return updated_owner


@router.delete('/exchange/{exchange_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_exchange_by_id(exchange_id: UUID, exchserv: ExchangeService = Depends(get_exch_service)):
    deleted_exchange =  await exchserv.delete_exchange_by_id(exchange_id)
    if deleted_exchange is None:
        raise NotFoundError(exchange_id, "Exchange")

    return deleted_exchange


@router.delete('/owner/{owner_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_owner_by_id(owner_id: UUID, exchserv: ExchangeService = Depends(get_exch_service)):
    deleted_owner =  await exchserv.delete_owner_by_id(owner_id)
    if deleted_owner is None:
        raise NotFoundError(owner_id, "Owner")

    return deleted_owner