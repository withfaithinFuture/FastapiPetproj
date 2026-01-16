from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.users import User
from src.models.shares import Share
from sqlalchemy.ext.asyncio import AsyncSession


class UserSharesRepository:
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
        
    async def add_shares(self, user: User, shares: list[Share]):
        self.session.add(user)
        self.session.add_all(shares)
        await self.session.flush()
        await self.session.refresh(user)

        return user


    async def get_shares_info(self):
        query = select(Share).options(selectinload(Share.owner_share))
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_user_by_id(self, upd_id: UUID):
        query = select(User).where(User.id == upd_id).with_for_update(skip_locked=True) #пропуск заблок id
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def get_share_by_id(self, upd_id: UUID):
        query = select(Share).where(Share.id == upd_id).with_for_update(skip_locked=True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def update_object(self, upd_object):
        await self.session.flush()
        await self.session.refresh(upd_object)
        return upd_object


    async def get_shares_or_user_by_id(self, obj_id: UUID):
        user = await self.session.get(User, obj_id).with_for_update(skip_locked=True)
        share = await self.session.get(Share, obj_id).with_for_update(skip_locked=True)
        return user, share


    async def delete_owner_or_share(self, delete_obj):
        await self.session.delete(delete_obj)