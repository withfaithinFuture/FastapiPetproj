from uuid import UUID
from fastapi import APIRouter, Depends
from src.services.schemas.shares_schemas import UserSchema, UserSchemaUpdate, SharesSchemaUpdate
from src.services.db.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.shares_service import SharesService


router = APIRouter()

def get_shares_service(session: AsyncSession = Depends(get_session)):
    return SharesService(session)


@router.post('/Shares/Add', tags=['Actions with shares'])
async def add_shares(user_data: UserSchema, shsrv: SharesService = Depends(get_shares_service)):
    return await shsrv.add_shares_service(user_data)


@router.get('/Shares/Get', tags=['Actions with shares'])
async def get_shares(shsrv: SharesService = Depends(get_shares_service)):
    return await shsrv.get_shares_info_service()


@router.patch('/Shares/UpdateOwner', tags=['Actions with shares'])
async def update_user_shares(user_id:UUID, update_data: UserSchemaUpdate, shsrv: SharesService = Depends(get_shares_service)):
    return await shsrv.update_user_shares_info_service(user_id, update_data)


@router.patch('/Shares/UpdateShare', tags=['Actions with shares'])
async def update_user_shares(share_id: UUID, update_data: SharesSchemaUpdate, shsrv: SharesService = Depends(get_shares_service)):
    return  await shsrv.update_share_info_service(share_id, update_data)


@router.post('/Shares/Delete', tags=['Actions with shares'])
async def delete_exchange(delete_id: UUID, shsrv: SharesService = Depends(get_shares_service)):
    return await shsrv.delete_owner_or_share(delete_id)
