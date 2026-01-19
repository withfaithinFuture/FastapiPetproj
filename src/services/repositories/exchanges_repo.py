from typing import Any, Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.exchange_owners import Owner
from src.models.exchanges import Exchange



class ExchangesOwnersRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def add_exchange(self, owner: Owner, exchange: Exchange) -> Exchange:
        self.session.add(owner)
        self.session.add(exchange)
        await self.session.flush()
        await self.session.refresh(exchange)

        return exchange


    async def get_exchanges_info(self):
        query = select(Exchange).options(selectinload(Exchange.owner))
        result = await self.session.execute(query)
        return result.scalars().all()


    async def update_exchange_info(self, exchange_id: UUID) -> Exchange | None:
        query = select(Exchange).where(exchange_id == Exchange.id).options(selectinload(Exchange.owner)).with_for_update(skip_locked=True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def update_object(self, upd_object):
        await self.session.flush()
        await self.session.refresh(upd_object)
        return upd_object


    async def update_owner_info(self, update_id: UUID) -> Owner | None:
        query = select(Owner).where(update_id == Owner.id).with_for_update(skip_locked=True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def get_exchange_or_owner_by_id(self, obj_id: UUID) -> tuple[Exchange | None, Owner | None]:
        exchange_query = select(Exchange).where(Exchange.id == obj_id).with_for_update(skip_locked=True)
        owner_query = select(Owner).where(Owner.id == obj_id).with_for_update(skip_locked=True)
        exchange_by_id = await self.session.execute(exchange_query)
        owner_by_id = await self.session.execute(owner_query)
        return exchange_by_id.scalar_one_or_none(), owner_by_id.scalar_one_or_none()


    async def delete_exchange_or_owner(self, delete_obj):
        await self.session.delete(delete_obj)
