import ujson
from arq import ArqRedis
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from uuid import UUID
from redis.asyncio import Redis
from src.models.exchange_owners import Owner
from src.models.exchanges import Exchange
from src.enums.saga_enums import SagaStatus
from src.schemas.exchange_owners_schemas import ExchangeOwnerUpdateSchema, ExchangeOwnerSchema
from src.schemas.exchange_schemas import ExchangeCreateSchema, ExchangeResponseSchema, ExchangeUpdateSchema, \
    MarketDataerviceValidationSchema
from src.client.market_data_client import MarketDataClient
from src.core.exceptions import NotFoundError, NotFoundByNameError, LocalDBError, SagaTransactionError
from src.repositories.exchanges_repo import ExchangesOwnersRepository as exch_rep
from src.app.config import settings


logger_exchange = logging.getLogger("services.exchange")

class ExchangeService:

    def __init__(self, session: AsyncSession, redis: Redis, market_data_client: MarketDataClient, arq_pool: ArqRedis = None):
        self.session = session
        self.exch_rep = exch_rep(self.session)
        self.redis = redis
        self.market_data_client = market_data_client
        self.exchange_key = settings.SERVICE_EXCHANGE_KEY
        self.arq_pool = arq_pool


    async def create_task_exchange_saga(self, exchange_data: ExchangeCreateSchema) -> ExchangeResponseSchema | dict:
        exchange_name = exchange_data.exchange_name
        existing_exchange = await self.exch_rep.get_exchange_by_name(exchange_name=exchange_name)

        if existing_exchange:
            if existing_exchange.status == SagaStatus.FINISHED:
                logger_exchange.info(f"Биржа {exchange_name} уже создана сагой")
                return ExchangeResponseSchema.model_validate(existing_exchange)

            if existing_exchange.status == SagaStatus.PENDING:
                raise LocalDBError(object_type="Exchange", object_name=exchange_name)

        exchange_dict = exchange_data.model_dump(exclude='owner')
        owner_dict = exchange_data.owner.model_dump()

        new_job = await self.arq_pool.enqueue_job(
            'run_create_exchange_saga',
            exchange_dict,
            owner_dict,
            self.exchange_key
        )

        return {
            "message": "Заявка на создание биржи принята",
            "job_id": new_job.job_id,
            "status": "PENDING"
        }


    async def get_exchanges_info_service(self) -> list[ExchangeResponseSchema]:
        logger_exchange.info("Запрос информации о биржах")

        cached_data = await self.redis.get(self.exchange_key)
        if cached_data:
            logger_exchange.info("Данные бирж получены из Redis")
            exch_data = ujson.loads(cached_data)
            return [ExchangeResponseSchema.model_validate(exch) for exch in exch_data]

        result_models = await self.exch_rep.get_exchanges_info()
        exchanges_schemas = [ExchangeResponseSchema.model_validate(exchange) for exchange in result_models]
        exch_data = [schema.model_dump() for schema in exchanges_schemas]
        json_data = ujson.dumps(exch_data)

        await self.redis.set(self.exchange_key, json_data, ex=3600)
        logger_exchange.info(f"Получено бирж: {len(exchanges_schemas)}")

        return exchanges_schemas


    async def get_exchange_by_name(self, exchange_name: str) -> ExchangeResponseSchema | None:
        logger_exchange.info("Получение биржи по ее названию")
        exchange_key = f"exchange:{exchange_name}"

        cached_data = await self.redis.get(exchange_key)
        if cached_data:
            logger_exchange.info("Данные биржи получены из Redis")
            result_model = ujson.loads(cached_data)
            return ExchangeResponseSchema.model_validate(result_model)

        result_model = await self.exch_rep.get_exchange_by_name(exchange_name=exchange_name)
        if result_model is None:
            logger_exchange.warning(f"Биржа не найдена в БД: {exchange_name}")
            raise NotFoundByNameError(exchange_name, 'Exchange')

        logger_exchange.info(f"Биржа найдена: name={exchange_name}")

        return ExchangeResponseSchema.model_validate(result_model)


    async def update_exchange_info_service(self, exchange_id: UUID, update_info: ExchangeUpdateSchema) -> ExchangeCreateSchema | None:
        logger_exchange.info(f"Обновление биржи: ID={exchange_id}")

        update_dict = update_info.model_dump(exclude_none=True, mode='json')
        existing_exchange = await self.exch_rep.get_exchange_by_id(exchange_id)

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
        exist_owner = await self.exch_rep.get_owner_by_id(owner_id)

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


    async def delete_exchange_by_id_service(self, exchange_id: UUID):
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


    async def delete_owner_by_id_service(self, owner_id: UUID):
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


    async def create_exchange_with_saga_service(self, exchange_data: ExchangeCreateSchema):
        logger_exchange.info("Сага - Создание биржи")

        owner_dict = exchange_data.owner.model_dump()
        exchange_dict = exchange_data.model_dump(exclude='owner')
        exchange_name = exchange_dict['exchange_name']

        existing_exchange = await self.exch_rep.get_exchange_by_name(exchange_name=exchange_name)
        if existing_exchange and existing_exchange.status == SagaStatus.FAILED:
            local_exchange = existing_exchange
            local_exchange.status = SagaStatus.ACTIVE

            await self.exch_rep.update_object(local_exchange)
            await self.exch_rep.session.commit()

        else:
            local_exchange = await self.create_local_exchange_service(owner_dict=owner_dict,
                                                                      exchange_dict=exchange_dict,
                                                                      exchange_name=exchange_name)

        additional_info = await self.get_market_data_client_info_service(exchange=local_exchange,
                                                                         exchange_name=exchange_name)

        final_exchange = await self.get_final_exchange_service(additional_exchange_data=additional_info,
                                                               exchange=local_exchange, exchange_name=exchange_name)

        await self.update_cache_service(exchange=final_exchange)

        logger_exchange.info(f"сага завершена, у биржи {exchange_name} статус - FINISHED")
        return ExchangeResponseSchema.model_validate(final_exchange)
    
    
    async def create_local_exchange_service(self, owner_dict: dict, exchange_dict: dict, exchange_name: str):
        owner = Owner(**owner_dict)
        exchange = Exchange(**exchange_dict)
        exchange.owner = owner
        exchange.status = SagaStatus.PENDING

        try:
            await self.exch_rep.create_exchange(owner=owner, exchange=exchange)
            exchange.status = SagaStatus.ACTIVE
            await self.exch_rep.session.commit()

            logger_exchange.info(f"Сага - успешная локальная транза, биржа - {exchange_name}")
            return exchange

        except Exception as e:
            logger_exchange.error(f"Сбой бд при начале саги: {e}")
            raise LocalDBError(object_type="Exchange", object_name=exchange_name)


    async def get_market_data_client_info_service(self, exchange: Exchange, exchange_name: str):
        try:
            logger_exchange.info(f"Сага - транзакция во 2 сервис-клиент")

            additional_exchange_data_dict = await self.market_data_client.create_additional_info(
                exchange_name=exchange_name)
            additional_exchange_data = MarketDataerviceValidationSchema.model_validate(additional_exchange_data_dict)

            logger_exchange.info("2 сервис ответил успешно")
            return additional_exchange_data

        except Exception as e:
            logger_exchange.error("Сага - ошибка 2 сервиса, откатываемся")

            exchange.status = SagaStatus.FAILED
            await self.exch_rep.update_object(exchange)
            await self.exch_rep.session.commit()

            raise SagaTransactionError(service_name="Market_Data_Service")


    async def get_final_exchange_service(self, additional_exchange_data: MarketDataerviceValidationSchema, exchange: Exchange, exchange_name: str):
        try:
            for key, value in additional_exchange_data.model_dump().items():
                if hasattr(exchange, key):
                    setattr(exchange, key, value)

            exchange.status = SagaStatus.FINISHED

            await self.exch_rep.update_object(exchange)
            await self.exch_rep.session.commit()

            logger_exchange.info(f"Сага успешно завершена для {exchange_name}")
            return exchange

        except Exception as e:
            logger_exchange.info(f"Локальная бд упала при сохранении: {e}")
            await self.market_data_client.delete_additional_info(exchange_name=exchange_name)
            logger_exchange.info("Мусор во 2 сервисе удален")

            raise LocalDBError(object_type="Exchange", object_name=exchange_name)


    async def update_cache_service(self, exchange: Exchange):
        try:
            exchanges_cache = await self.redis.get(self.exchange_key)
            if exchanges_cache:
                exchanges_list = ujson.loads(exchanges_cache)
                new_exchange_schema = ExchangeResponseSchema.model_validate(exchange)
                new_exchange_dict = new_exchange_schema.model_dump(mode='json')

                exchanges_list.append(new_exchange_dict)

                await self.redis.set(self.exchange_key, ujson.dumps(exchanges_list), ex=3600)
                logger_exchange.info("Новая биржа добавлена в кэш")

        except Exception as e:
            logger_exchange.error(f"кэш в саге не обновился из-за ошибки: {e}")
            await self.redis.delete(self.exchange_key)