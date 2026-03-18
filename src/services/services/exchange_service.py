import ujson
from sqlalchemy.ext.asyncio import AsyncSession
import json
import logging
from uuid import UUID
from redis.asyncio import Redis
from services.services.exchange_orchestrator import SaveExchangeOrchestrator
from src.client.second_client import SecondClient
from src.services.schemas.exchange_owners_schemas import ExchangeOwnerUpdateSchema
from src.services.core.exceptions import NotFoundError, NotFoundByNameError
from src.services.schemas.exchange_schemas import ExchangeCreateSchema, ExchangeUpdateSchema, \
    ExchangeOwnerSchema, ExchangeResponseSchema, SecondServiceValidationSchema
from src.services.repositories.exchanges_repo import ExchangesOwnersRepository as exch_rep


logger_exchange = logging.getLogger("services.exchange")

class ExchangeService:

    def __init__(self, session: AsyncSession, redis: Redis, second_service_client: SecondClient, exchange_key: str):
        self.session = session
        self.exch_rep = exch_rep(self.session)
        self.redis = redis
        self.second_service_client = second_service_client
        self.exchange_key = exchange_key
        self.orchestrator = SaveExchangeOrchestrator(exchange_repo=self.exch_rep, second_client=self.second_service_client, redis=self.redis)


    async def create_exchange_service(self, exchange_data: ExchangeCreateSchema) -> ExchangeResponseSchema:

        return await self.orchestrator.create_exchange_with_saga(exchange_data=exchange_data, exchange_key=self.exchange_key)



    async def get_exchanges_info_service(self) -> list[ExchangeResponseSchema]:
        logger_exchange.info("Запрос информации о биржах")

        cached_data = await self.redis.get(self.exchange_key)
        if cached_data:
            logger_exchange.info("Данные бирж получены из Redis")
            exch_data = json.loads(cached_data)
            return [ExchangeResponseSchema.model_validate(exch) for exch in exch_data]

        result_models = await self.exch_rep.get_exchanges_info()
        exchanges_schemas = [ExchangeResponseSchema.model_validate(exchange) for exchange in result_models]
        exch_data = [schema.model_dump() for schema in exchanges_schemas]
        json_data = json.dumps(exch_data, default=str)

        await self.redis.set(self.exchange_key, json_data, ex=3600)
        logger_exchange.info(f"Получено бирж: {len(exchanges_schemas)}")

        return exchanges_schemas


    async def get_exchange_by_name(self, exchange_name: str) -> ExchangeResponseSchema | None:
        logger_exchange.info("Получение биржи по ее названию")
        exchange_key = f"exchange:{exchange_name}"

        cached_data = await self.redis.get(exchange_key)
        if cached_data:
            logger_exchange.info("Данные биржи получены из Redis")
            old_data_dict = json.loads(cached_data)

        else:
            result_model = await self.exch_rep.get_exchange_by_name(exchange_name=exchange_name)

            if result_model is None:
                logger_exchange.warning(f"Биржа не найдена: {exchange_name}")
                raise NotFoundByNameError(exchange_name, 'Exchange')

            old_data_dict = ExchangeResponseSchema.model_validate(result_model).model_dump()
            json_data = json.dumps(old_data_dict, default=str)

            await self.redis.set(exchange_key, json_data, ex=3600)

        fresh_additional_data_dict = await self.second_service_client.get_additional_info(exchange_name=exchange_name)
        fresh_additional_data = SecondServiceValidationSchema.model_validate(fresh_additional_data_dict)

        new_exchange_model = old_data_dict | fresh_additional_data.model_dump()
        logger_exchange.info(f"Биржа найдена: name={exchange_name}")

        return ExchangeResponseSchema(**new_exchange_model)


    async def update_exchange_info_service(self, exchange_id: UUID, update_info: ExchangeUpdateSchema) -> ExchangeCreateSchema | None:
        logger_exchange.info(f"Обновление биржи: ID={exchange_id}")

        update_dict = update_info.model_dump(exclude_none=True, mode='json')
        existing_exchange = await self.exch_rep.update_exchange_info(exchange_id)

        if existing_exchange is None:
            logger_exchange.warning(f"Биржа не найдена: ID={exchange_id}")
            raise NotFoundError(exchange_id, "exchange")

        for key, value in update_dict.items():
            if hasattr(existing_exchange, key):
                setattr(existing_exchange, key, value)

        await self.exch_rep.update_object(existing_exchange)

        try:
            named_exchange_key = f"exchange:{existing_exchange.exchange_name}"
            cached_data = await self.redis.get(named_exchange_key)
            if cached_data:
                exchange_dict = ujson.loads(cached_data)
                exchange_dict.update(update_dict)

                await self.redis.set(named_exchange_key, ujson.dumps(exchange_dict), ex=3600)

            exchanges_cache = await self.redis.get(self.exchange_key)
            if exchanges_cache:
                exchanges_list = ujson.loads(exchanges_cache)
                for exchange in exchanges_list:
                    if exchange.get('id') == str(exchange_id):
                        exchange.update(update_dict)
                        break
                await self.redis.set(self.exchange_key, ujson.dumps(exchanges_list), ex=3600)

            logger_exchange.info(f"Биржа обновлена: ID={exchange_id}")

        except Exception as e:
            logger_exchange.error(f"Ошибка при обновлении кэша биржи: {e}")

            await self.redis.delete(self.exchange_key)
            await self.redis.delete(f"exchange:{existing_exchange.exchange_name}")

        return ExchangeCreateSchema.model_validate(existing_exchange)


    async def update_owner_info_service(self, owner_id: UUID, update_info: ExchangeOwnerUpdateSchema) -> ExchangeOwnerSchema | None:
        logger_exchange.info(f"Обновление владельца: ID={owner_id}")

        update_info_dict = update_info.model_dump(exclude_none=True, mode='json')
        exist_owner = await self.exch_rep.update_owner_info(owner_id)

        if exist_owner is None:
            logger_exchange.warning(f"Владелец не найден: ID={owner_id}")
            raise NotFoundError(owner_id, "owner")

        for key, value in update_info_dict.items():
            if hasattr(exist_owner, key):
                setattr(exist_owner, key, value)

        await self.exch_rep.update_object(exist_owner)

        try:
            exchange_name = exist_owner.exchange.exchange_name
            named_exchange_key = f"exchange:{exchange_name}"

            cached_data = await self.redis.get(named_exchange_key)
            if cached_data:
                exchange_dict = ujson.loads(cached_data)
                exchange_dict['owner'].update(update_info_dict)
                await self.redis.set(named_exchange_key, ujson.dumps(exchange_dict), ex=3600)

            exchanges_cache = await self.redis.get(self.exchange_key)
            if exchanges_cache:
                exchanges_list = ujson.loads(exchanges_cache)
                for exchange in exchanges_list:
                    owner_dict = exchange.get('owner')
                    if owner_dict['id'] == str(owner_id):
                        owner_dict.update(update_info_dict)
                        break
                await self.redis.set(self.exchange_key, ujson.dumps(exchanges_list), ex=3600)

            logger_exchange.info(f"Обновление владельца: ID={owner_id}")

        except Exception as e:
            logger_exchange.error(f"Ошибка при обновлении кэша владельца: {e}")
            await self.redis.delete(self.exchange_key)
            await self.redis.delete(f"exchange:{exist_owner.exchange.exchange_name}")

        logger_exchange.info(f"Владелец обновлен: ID={owner_id}")

        return ExchangeOwnerSchema.model_validate(exist_owner)


    async def delete_exchange_by_id(self, exchange_id: UUID):
        exchange_by_id = await self.exch_rep.get_exchange_by_id(exchange_id)

        if exchange_by_id is None:
            logger_exchange.warning(f"Биржа не найдена для удаления: ID={exchange_id}")
            raise NotFoundError(exchange_id, "Exchange")

        logger_exchange.info(f"Найдена биржа для удаления: ID={exchange_id}")
        await self.exch_rep.delete_exchange_or_owner(exchange_by_id)
        await self.redis.delete(self.exchange_key)
        await self.redis.delete(f"exchange:{exchange_by_id.exchange_name}")
        logger_exchange.info(f"Биржа удалена: ID={exchange_id}")

        return True


    async def delete_owner_by_id(self, owner_id: UUID):
        owner_by_id = await self.exch_rep.get_owner_by_id(owner_id)

        if owner_by_id is None:
            logger_exchange.warning(f"Владелец не найден для удаления: ID={owner_id}")
            raise NotFoundError(owner_id, "Owner")

        logger_exchange.info(f"Найден владелец для удаления: ID={owner_id}")
        await self.exch_rep.delete_exchange_or_owner(owner_by_id)
        await self.redis.delete(self.exchange_key)
        await self.redis.delete(f"exchange:{owner_by_id.exchange.exchange_name}")
        logger_exchange.info(f"Владелец удален: ID={owner_id}")

        return True