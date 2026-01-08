from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.services.exceptions import NothingExists
from src.models.exchange_owners import Owner
from src.models.exchanges import Exchange
from src.services.schemas.schemas import ExchangeSchema, ExchangeUpdateSchema, ExchangeOwnerUpdateSchema, \
    ExchangeOwnerSchema


class ExchangesOwnersRepository:
    @classmethod
    async def add_exchange(cls, exchange_data: ExchangeSchema, db_session: AsyncSession):
        owner_data_dict, exchange_data_dict = exchange_data.owner.model_dump(), exchange_data.model_dump(exclude='owner')
        owner, exchange = Owner(**owner_data_dict), Exchange(**exchange_data_dict)
        exchange.owner = owner

        db_session.add(owner)
        db_session.add(exchange)
        await db_session.flush()
        await db_session.refresh(exchange)

        return exchange


    @classmethod
    async def get_exchanges_info(cls, db_session: AsyncSession):
        query = select(Exchange).options(selectinload(Exchange.owner))
        result = await db_session.execute(query)
        result_models = result.scalars().all()
        exchanges = [ExchangeSchema.model_validate(exchange) for exchange in result_models]
        return exchanges


    @classmethod
    async def update_exchange_info(cls, update_info: ExchangeUpdateSchema, db_session: AsyncSession):
        update_dict = update_info.model_dump(exclude_none=True)
        query = select(Exchange).where(update_dict['id'] == Exchange.id).options(selectinload(Exchange.owner))
        result = await db_session.execute(query)
        existing_exchange = result.scalar_one_or_none()

        for key, value in update_dict.items():
            if hasattr(existing_exchange, key):
                setattr(existing_exchange, key, value)

        await db_session.flush()
        await db_session.refresh(existing_exchange)

        return ExchangeSchema.model_validate(existing_exchange)


    @classmethod
    async def update_owner_info(cls, update_info: ExchangeOwnerUpdateSchema, db_session: AsyncSession):
        update_info_dict = update_info.model_dump(exclude_none=True)
        query = select(Owner).where(update_info_dict['id'] == Owner.id)
        result = await db_session.execute(query)
        exist_owner = result.scalar_one_or_none()

        for key, value in update_info_dict.items():
            if hasattr(exist_owner, key):
                setattr(exist_owner, key, value)

        await db_session.flush()
        await db_session.refresh(exist_owner)

        return ExchangeOwnerSchema.model_validate(exist_owner)


    @classmethod
    async def delete_exchange_info(cls, object_id: UUID, db_session: AsyncSession):
        exchange_by_id = await db_session.get(Exchange, object_id)
        if exchange_by_id is not None:
            await db_session.delete(exchange_by_id)
            return exchange_by_id

        owner = await db_session.get(Owner, object_id)

        if owner is not None:
            owner = await db_session.get(Owner, object_id)
            await db_session.delete(owner)
            return owner

        else:
            raise NothingExists(object_id, f"Биржи или создателя с ID = {object_id} не существует! Введите корректный ID!")

