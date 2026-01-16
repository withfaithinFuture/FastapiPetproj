import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.core.exceptions import ValidationError
from src.models.exchange_owners import Owner
from src.models.exchanges import Exchange
from src.services.schemas.exchange_schemas import ExchangeSchema, ExchangeUpdateSchema, ExchangeOwnerUpdateSchema, \
    ExchangeOwnerSchema
from src.services.repositories.exchanges_repo import ExchangesOwnersRepository as ExchRep


logger_exchange = logging.getLogger("services.exchange")

class ExchangeService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.ExchRep = ExchRep(self.session)


    async def add_exchange_service(self, exchange_data: ExchangeSchema):
        logger_exchange.info("Добавление биржи с владельцем")

        owner_data_dict, exchange_data_dict = exchange_data.owner.model_dump(), exchange_data.model_dump(exclude='owner')
        owner, exchange = Owner(**owner_data_dict), Exchange(**exchange_data_dict)
        exchange.owner = owner

        await self.ExchRep.add_exchange(owner, exchange)
        logger_exchange.info(f"Биржа добавлена: ID={exchange.id}")

        return ExchangeSchema.model_validate(exchange)


    async def get_exchanges_info_service(self):
        logger_exchange.info("Запрос информации о биржах")
        result_models = await self.ExchRep.get_exchanges_info()
        exchanges_schemas = [ExchangeSchema.model_validate(exchange) for exchange in result_models]
        logger_exchange.info(f"Получено бирж: {len(exchanges_schemas)}")
        return exchanges_schemas


    async def update_exchange_info_service(self, exchange_id: UUID, update_info: ExchangeUpdateSchema):
        logger_exchange.info(f"Обновление биржи: ID={exchange_id}")

        update_dict = update_info.model_dump(exclude_none=True)
        existing_exchange = await self.ExchRep.update_exchange_info(exchange_id)

        if existing_exchange is None:
            logger_exchange.warning(f"Биржа не найдена: ID={exchange_id}")
            raise ValidationError(exchange_id, "exchange")

        for key, value in update_dict.items():
            if hasattr(existing_exchange, key):
                setattr(existing_exchange, key, value)

        await self.ExchRep.update_object(existing_exchange)
        logger_exchange.info(f"Биржа обновлена: ID={exchange_id}")

        return ExchangeSchema.model_validate(existing_exchange)


    async def update_owner_info_service(self, owner_id: UUID, update_info: ExchangeOwnerUpdateSchema):
        logger_exchange.info(f"Обновление владельца: ID={owner_id}")

        update_info_dict = update_info.model_dump(exclude_none=True)
        exist_owner = await self.ExchRep.update_owner_info(owner_id)

        if exist_owner is None:
            logger_exchange.warning(f"Владелец не найден: ID={owner_id}")
            raise ValidationError(owner_id, "owner")

        for key, value in update_info_dict.items():
            if hasattr(exist_owner, key):
                setattr(exist_owner, key, value)

        await self.ExchRep.update_object(exist_owner)
        logger_exchange.info(f"Владелец обновлен: ID={owner_id}")

        return ExchangeOwnerSchema.model_validate(exist_owner)


    async def delete_exchange_info_service(self, object_id: UUID):
        logger_exchange.info(f"Удаление объекта: ID={object_id}")
        exchange, owner = await self.ExchRep.get_exchange_or_owner_by_id(object_id)

        if exchange is not None:
            logger_exchange.info(f"Найдена биржа для удаления: ID={object_id}, name={exchange.name}")
            await self.ExchRep.delete_exchange_or_owner(exchange)
            logger_exchange.info(f"Биржа удалена: ID={object_id}")
            return exchange

        if owner is not None:
            logger_exchange.info(f"Найден владелец для удаления: ID={object_id}, name={owner.name}")
            await self.ExchRep.delete_exchange_or_owner(owner)
            logger_exchange.info(f"Владелец удален: ID={object_id}")
            return owner

        else:
            logger_exchange.warning(f"Объект не найден: ID={object_id} (ни биржа, ни владелец)")
            raise  ValidationError(object_id,"exchange_or_owner")
