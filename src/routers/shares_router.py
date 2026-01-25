from uuid import UUID
from fastapi import APIRouter, Depends, status
from src.services.schemas.shares_schemas import UserSchema, UserSchemaUpdate, SharesSchemaUpdate
from src.app.dependencies import get_shares_service
from services.services.shares_service import SharesService


router = APIRouter(tags=['Actions with shares'])

@router.post('/shares', status_code=status.HTTP_201_CREATED)
async def create_shares(user_data: UserSchema, shsrv: SharesService = Depends(get_shares_service)):
    return await shsrv.create_shares_service(user_data)


@router.get('/shares', status_code=status.HTTP_201_CREATED)
async def get_shares(shsrv: SharesService = Depends(get_shares_service)):
    return await shsrv.get_shares_info_service()


@router.patch('/shares/{user_id}', status_code=status.HTTP_201_CREATED)
async def update_user_shares(user_id:UUID, update_data: UserSchemaUpdate, shsrv: SharesService = Depends(get_shares_service)):
    return await shsrv.update_user_shares_info_service(user_id, update_data)


@router.patch('/shares/{share_id}', status_code=status.HTTP_201_CREATED)
async def update_user_shares(share_id: UUID, update_data: SharesSchemaUpdate, shsrv: SharesService = Depends(get_shares_service)):
    return  await shsrv.update_share_info_service(share_id, update_data)


@router.delete('/shares/{share_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_share_by_id(share_id: UUID, shsrv: SharesService = Depends(get_shares_service)):
    return await shsrv.delete_share_by_id(share_id)


@router.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_owner_by_id(user_id: UUID, shsrv: SharesService = Depends(get_shares_service)):
    return await shsrv.delete_user_by_id(user_id)