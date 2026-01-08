from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.services.exceptions import NothingExists
from src.models.users import User
from src.models.shares import Share
from src.services.schemas.schemas import UserSchema, UserSchemaUpdate, SharesSchemaUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.repositories.ready_info import ReadyInfoForAddRepo


class UserSharesRepository:
    @classmethod
    async def add_shares(cls, user_data: UserSchema, db_session: AsyncSession):
        user, shares = ReadyInfoForAddRepo.ready_info_shares(user_data)
        user.user_shares = shares

        db_session.add(user)
        db_session.add_all(shares)

        await db_session.flush()
        await db_session.refresh(user)

        return UserSchema.model_validate(user_data)


    @classmethod
    async def get_shares_info(cls, db_session: AsyncSession):
        query = select(Share).options(selectinload(Share.owner_share))
        result = await db_session.execute(query)
        result_scalar = result.scalars().all()

        return result_scalar


    @classmethod
    async def update_user_shares_info(cls, update_data: UserSchemaUpdate, db_session: AsyncSession):
        update_data_dict = update_data.model_dump(exclude_none=True)
        query = select(User).where(User.id == update_data_dict['id'])
        result = await db_session.execute(query)
        existing_user = result.scalar_one_or_none()

        for key, value in update_data_dict.items():
            if hasattr(existing_user, key):
                setattr(existing_user, key, value)

        await db_session.flush()
        await db_session.refresh(existing_user)

        return UserSchemaUpdate.model_validate(existing_user)


    @classmethod
    async def update_shares_info(cls, update_info: SharesSchemaUpdate, db_session: AsyncSession):
        update_info_dict = update_info.model_dump(exclude_none=True)
        query = select(Share).where(Share.id == update_info_dict['id'])
        result = await db_session.execute(query)
        existing_share = result.scalar_one_or_none()

        for key, value in update_info_dict.items():
            if hasattr(existing_share, key):
                setattr(existing_share, key, value)


        await db_session.flush()
        await db_session.refresh(existing_share)

        return SharesSchemaUpdate.model_validate(existing_share)


    @classmethod
    async def delete_owner_or_share(cls, delete_id: UUID, db_session: AsyncSession):
        existing_user = await db_session.get(User, delete_id)

        if existing_user is not None:
            await db_session.delete(existing_user)
            return existing_user

        existing_share = await db_session.get(Share, delete_id)
        if existing_share is not None:
            await db_session.delete(existing_share)
            return existing_share

        else:
            raise NothingExists(delete_id, f"Акций или юзера с ID = {delete_id} не существует! Введите корректный ID!")