from typing import Sequence, Any, Optional, Union, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.users import User
from src.models.shares import Share
from sqlalchemy.ext.asyncio import AsyncSession


class UserSharesRepository:
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
        
    async def create_shares(self, user: User, shares: list[Share]) -> User:
        self.session.add(user)
        self.session.add_all(shares)
        await self.session.flush()
        await self.session.refresh(user)

        return user


    async def get_shares_info(self) -> List[Share]:
        query = select(User).options(selectinload(User.user_shares))
        result = await self.session.execute(query)
        return list(result.scalars().all())


    async def get_user_by_id(self, upd_id: UUID) -> Optional[User]:
        query = select(User).where(User.id == upd_id).with_for_update(skip_locked=True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def get_share_by_id(self, upd_id: UUID) -> Optional[Share]:
        query = select(Share).where(Share.id == upd_id).with_for_update(skip_locked=True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def update_object(self, upd_object) -> Union[User, Share]:
        await self.session.flush()
        await self.session.refresh(upd_object)
        return upd_object


    async def delete_user_or_share(self, delete_obj) -> None:
        await self.session.delete(delete_obj)