from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.users import User
from src.models.shares import Share
from sqlalchemy.ext.asyncio import AsyncSession


class UserSharesRepository:
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
        
    async def add_shares(self, user: User, shares: list[Share]) -> User:
        self.session.add(user)
        self.session.add_all(shares)
        await self.session.flush()
        await self.session.refresh(user)

        return user


    async def get_shares_info(self):
        query = select(Share).options(selectinload(Share.owner_share))
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_user_by_id(self, upd_id: UUID) -> User | None:
        query = select(User).where(User.id == upd_id).with_for_update(skip_locked=True) #пропуск заблок id
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def get_share_by_id(self, upd_id: UUID) -> Share | None:
        query = select(Share).where(Share.id == upd_id).with_for_update(skip_locked=True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def update_object(self, upd_object):
        await self.session.flush()
        await self.session.refresh(upd_object)
        return upd_object


    async def get_shares_or_user_by_id(self, obj_id: UUID) -> tuple[User | None, Share | None]:
        user_query = select(User).where(User.id == obj_id).with_for_update(skip_locked=True)
        share_query = select(Share).where(Share.id == obj_id).with_for_update(skip_locked=True)
        user = await self.session.execute(user_query)
        share = await self.session.execute(share_query)
        return user.scalar_one_or_none(), share.scalar_one_or_none()


    async def delete_owner_or_share(self, delete_obj):
        await self.session.delete(delete_obj)