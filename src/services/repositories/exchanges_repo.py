from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.exchange_owners import Owner
from src.models.exchanges import Exchange



class ExchangesOwnersRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def add_exchange(self, owner: Owner, exchange: Exchange):
        self.session.add(owner)
        self.session.add(exchange)
        await self.session.flush()
        await self.session.refresh(exchange)

        return exchange


    async def get_exchanges_info(self):
        query = select(Exchange).options(selectinload(Exchange.owner))
        result = await self.session.execute(query)
        return result.scalars().all()


    async def update_exchange_info(self, exchange_id: UUID):
        query = select(Exchange).where(exchange_id == Exchange.id).options(selectinload(Exchange.owner)).with_for_update(skip_locked=True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def update_object(self, upd_object):
        await self.session.flush()
        await self.session.refresh(upd_object)
        return upd_object


    async def update_owner_info(self, update_id: UUID):
        query = select(Owner).where(update_id == Owner.id).with_for_update(skip_locked=True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def get_exchange_or_owner_by_id(self, obj_id: UUID):
        exchange_by_id = await self.session.get(Exchange, obj_id).with_for_update(skip_locked=True)
        owner_by_id = await self.session.get(Owner, obj_id).with_for_update(skip_locked=True)
        return exchange_by_id, owner_by_id


    async def delete_exchange_or_owner(self, delete_obj):
        await self.session.delete(delete_obj)
