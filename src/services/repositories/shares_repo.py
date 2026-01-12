from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.users import User
from src.models.shares import Share
from sqlalchemy.ext.asyncio import AsyncSession


class UserSharesRepository:
    @classmethod
    async def add_shares(cls, user: User, shares: list[Share], db_session: AsyncSession):
        db_session.add(user)
        db_session.add_all(shares)
        await db_session.flush()
        await db_session.refresh(user)

        return user


    @classmethod
    async def get_shares_info(cls, db_session: AsyncSession):
        query = select(Share).options(selectinload(Share.owner_share))
        result = await db_session.execute(query)
        return result.scalars().all()


    @classmethod
    async def get_user_by_id(cls, upd_id: UUID, db_session: AsyncSession):
        query = select(User).where(User.id == upd_id).with_for_update(skip_locked=True) #пропуск заблок id
        result = await db_session.execute(query)
        return result.scalar_one_or_none()


    @classmethod
    async def get_share_by_id(cls, upd_id: UUID, db_session: AsyncSession):
        query = select(Share).where(Share.id == upd_id).with_for_update(skip_locked=True)
        result = await db_session.execute(query)
        return result.scalar_one_or_none()


    @classmethod
    async def update_object(cls, upd_object, db_session: AsyncSession):
        await db_session.flush()
        await db_session.refresh(upd_object)
        return upd_object


    @classmethod
    async def get_shares_or_user_by_id(cls, obj_id: UUID, db_session: AsyncSession):
        user = await db_session.get(User, obj_id).with_for_update(skip_locked=True)
        share = await db_session.get(Share, obj_id).with_for_update(skip_locked=True)
        return user, share


    @classmethod
    async def delete_owner_or_share(cls, delete_obj, db_session: AsyncSession):
        await db_session.delete(delete_obj)
        return delete_obj