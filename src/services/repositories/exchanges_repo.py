from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.exchange_owners import Owner
from src.models.exchanges import Exchange



class ExchangesOwnersRepository:
    @classmethod
    async def add_exchange(cls, owner: Owner, exchange: Exchange, db_session: AsyncSession):
        db_session.add(owner)
        db_session.add(exchange)
        await db_session.flush()
        await db_session.refresh(exchange)

        return exchange


    @classmethod
    async def get_exchanges_info(cls, db_session: AsyncSession):
        query = select(Exchange).options(selectinload(Exchange.owner))
        result = await db_session.execute(query)
        return result.scalars().all()


    @classmethod
    async def update_exchange_info(cls, exchange_id: UUID, db_session: AsyncSession):
        query = select(Exchange).where(exchange_id == Exchange.id).options(selectinload(Exchange.owner)).with_for_update(skip_locked=True)
        result = await db_session.execute(query)
        return result.scalar_one_or_none()


    @classmethod
    async def update_object(cls, upd_object, db_session: AsyncSession):
        await db_session.flush()
        await db_session.refresh(upd_object)
        return upd_object


    @classmethod
    async def update_owner_info(cls, update_id: UUID, db_session: AsyncSession):
        query = select(Owner).where(update_id == Owner.id).with_for_update(skip_locked=True)
        result = await db_session.execute(query)
        return result.scalar_one_or_none()


    @classmethod
    async def get_exchange_or_owner_by_id(cls, obj_id: UUID, db_session: AsyncSession):
        exchange_by_id = await db_session.get(Exchange, obj_id).with_for_update(skip_locked=True)
        owner_by_id = await db_session.get(Owner, obj_id).with_for_update(skip_locked=True)
        return exchange_by_id, owner_by_id


    @classmethod
    async def delete_exchange_or_owner(cls, delete_obj, db_session: AsyncSession):
        await db_session.delete(delete_obj)
        return delete_obj

