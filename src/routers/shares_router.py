from uuid import UUID
from fastapi import APIRouter, Depends
from src.services.schemas.shares_schemas import UserSchema, UserSchemaUpdate, SharesSchemaUpdate
from src.services.db.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.shares_service import SharesService as ShSrv


router = APIRouter()


@router.post('/Акции/Добавление акций с их владельцем', tags=['Действия с акциями'])
async def add_shares(user_data: UserSchema, db_session: AsyncSession = Depends(get_session)):
    new_data = await ShSrv.add_shares_service(user_data, db_session)
    return {'Shares': new_data, 'HTTP status': 201}


@router.get('/Акции/Получение акций с их владельцем', tags=['Действия с акциями'])
async def get_shares(db_session: AsyncSession = Depends(get_session)):
    all_data = await ShSrv.get_shares_info_service(db_session)
    return {'All data': all_data, 'HTTP status': 200}


@router.patch('/Акции/Обновление информации владельца акций', tags=['Действия с акциями'])
async def update_user_shares(user_id:UUID, update_data: UserSchemaUpdate, db_session: AsyncSession = Depends(get_session)):
    updated_user = await ShSrv.update_user_shares_info_service(user_id, update_data, db_session)
    return  {'New user info': updated_user, 'HTTP status': 200}


@router.patch('/Акции/Обновление информации акций', tags=['Действия с акциями'])
async def update_user_shares(share_id: UUID, update_data: SharesSchemaUpdate, db_session: AsyncSession = Depends(get_session)):
    updated_share = await ShSrv.update_share_info_service(share_id, update_data, db_session)
    return  {'New user info': updated_share, 'HTTP status': 200}


@router.post('/Акции/Удаление юзера или акций', tags=['Действия с акциями'])
async def delete_exchange(delete_id: UUID, db_session: AsyncSession = Depends(get_session)):
    deleted_object = await ShSrv.delete_owner_or_share(delete_id, db_session)
    return  {'Deleted object': deleted_object, 'HTTP status': 200}