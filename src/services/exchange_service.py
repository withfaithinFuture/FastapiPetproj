from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.core.exceptions import NothingExists, ValidationError
from src.models.exchange_owners import Owner
from src.models.exchanges import Exchange
from src.services.schemas.exchange_schemas import ExchangeSchema, ExchangeUpdateSchema, ExchangeOwnerUpdateSchema, \
    ExchangeOwnerSchema
from src.services.repositories.exchanges_repo import ExchangesOwnersRepository as ExchRep


class ExchangeService:
    @classmethod
    async def add_exchange_service(cls, exchange_data: ExchangeSchema, db_session: AsyncSession):
        owner_data_dict, exchange_data_dict = exchange_data.owner.model_dump(), exchange_data.model_dump(exclude='owner')
        owner, exchange = Owner(**owner_data_dict), Exchange(**exchange_data_dict)
        exchange.owner = owner

        await ExchRep.add_exchange(owner, exchange, db_session)
        return ExchangeSchema.model_validate(exchange)


    @classmethod
    async def get_exchanges_info_service(cls, db_session: AsyncSession):
        result_models = await ExchRep.get_exchanges_info(db_session)
        exchanges_schemas = [ExchangeSchema.model_validate(exchange) for exchange in result_models]
        return exchanges_schemas


    @classmethod
    async def update_exchange_info_service(cls, exchange_id: UUID, update_info: ExchangeUpdateSchema, db_session: AsyncSession):
        update_dict = update_info.model_dump(exclude_none=True)
        existing_exchange = await ExchRep.update_exchange_info(exchange_id, db_session)

        if existing_exchange is None:
            raise ValidationError(exchange_id,
                                  f"Биржи с таким ID = {exchange_id} не существует! Введите корректный ID!")

        for key, value in update_dict.items():
            if hasattr(existing_exchange, key):
                setattr(existing_exchange, key, value)

        await ExchRep.update_object(existing_exchange, db_session)
        return ExchangeSchema.model_validate(existing_exchange)


    @classmethod
    async def update_owner_info_service(cls, owner_id: UUID, update_info: ExchangeOwnerUpdateSchema, db_session: AsyncSession):
        update_info_dict = update_info.model_dump(exclude_none=True)
        exist_owner = await ExchRep.update_owner_info(owner_id, db_session)

        if exist_owner is None:
            raise ValidationError(owner_id,
                                  f"Создателя биржи с таким ID = {owner_id} не существует! Введите корректный ID!")

        for key, value in update_info_dict.items():
            if hasattr(exist_owner, key):
                setattr(exist_owner, key, value)

        await ExchRep.update_object(exist_owner, db_session)
        return ExchangeOwnerSchema.model_validate(exist_owner)


    @classmethod
    async def delete_exchange_info_service(cls, object_id: UUID, db_session: AsyncSession):
        exchange, owner = await ExchRep.get_exchange_or_owner_by_id(object_id, db_session)

        if exchange is not None:
            await ExchRep.delete_exchange_or_owner(exchange, db_session)
            return exchange

        if owner is not None:
            await ExchRep.delete_exchange_or_owner(owner, db_session)
            return owner

        else:
            raise NothingExists(object_id, f"Биржи или создателя с ID = {object_id} не существует! Введите корректный ID!")
