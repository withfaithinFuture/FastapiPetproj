import logging
import ujson
from redis.asyncio import Redis
from src.models.exchanges import SagaStatus
from src.services.schemas.exchange_schemas import ExchangeResponseSchema, ExchangeCreateSchema, \
    MarketDataerviceValidationSchema
from src.services.core.exceptions import SagaTransactionError, LocalDBError
from src.models.exchange_owners import Owner
from src.models.exchanges import Exchange
from src.client.market_data_client import MarketDataClient
from src.services.repositories.exchanges_repo import ExchangesOwnersRepository


logger_saga = logging.getLogger("saga_orch")

class ExchangeOrchestratorService:

    def __init__(self, exchange_repo: ExchangesOwnersRepository, market_data_client: MarketDataClient, redis: Redis):
        self.exchange_repo = exchange_repo
        self.market_data_client = market_data_client
        self.redis = redis


    async def create_exchange_with_saga(self, exchange_data: ExchangeCreateSchema, exchange_key: str):
        logger_saga.info("Сага - Создание биржи")

        owner_dict = exchange_data.owner.model_dump()
        exchange_dict = exchange_data.model_dump(exclude='owner')

        existing_exchange = await self.exchange_repo.get_exchange_by_name(exchange_name=exchange_dict['exchange_name'])
        if existing_exchange:
            if existing_exchange.status == SagaStatus.FINISHED:
                logger_saga.info(f"Биржа {exchange_dict['exchange_name']} уже создана сагой")
                return ExchangeResponseSchema.model_validate(existing_exchange)

            if existing_exchange.status == SagaStatus.PENDING:
                raise LocalDBError(object_type="Exchange", object_name=exchange_dict['exchange_name'])

            elif existing_exchange.status == SagaStatus.FAILED:
                exchange = existing_exchange
                exchange.status = SagaStatus.PENDING

                await self.exchange_repo.update_object(exchange)
                await self.exchange_repo.session.commit()

        else:
            owner = Owner(**owner_dict)
            exchange = Exchange(**exchange_dict)
            exchange.owner = owner
            exchange.status = SagaStatus.PENDING

            try:
                await self.exchange_repo.create_exchange(owner=owner, exchange=exchange)
                await self.exchange_repo.session.commit()
                exchange.status = SagaStatus.ACTIVE

                logger_saga.info(f"Сага - успешная локальная транза, биржа - {exchange_dict['exchange_name']}")

            except Exception as e:
                logger_saga.error(f"Сбой бд при начале саги: {e}")
                raise LocalDBError(object_type="Exchange", object_name=exchange_dict['exchange_name'])


        try:
            logger_saga.info(f"Сага - транзакция во 2 сервис-клиент")
            additional_exchange_data_dict = await self.market_data_client.create_additional_info(exchange_name=exchange_dict['exchange_name'])
            additional_exchange_data = MarketDataerviceValidationSchema.model_validate(additional_exchange_data_dict)
            logger_saga.info("2 сервис ответил успешно")

        except Exception as e:
            logger_saga.error("Сага - ошибка 2 сервиса, откатываемся")
            exchange.status = SagaStatus.FAILED
            await self.exchange_repo.update_object(exchange)
            await self.exchange_repo.session.commit()

            raise SagaTransactionError(service_name="Market_Data_Service")


        try:
            for key, value in additional_exchange_data.model_dump().items():
                if hasattr(exchange, key):
                    setattr(exchange, key, value)

            exchange.status = SagaStatus.FINISHED

            await self.exchange_repo.update_object(exchange)
            await self.exchange_repo.session.commit()

            logger_saga.info(f"Сага успешно завершена для {exchange_dict['exchange_name']}")

        except Exception as e:
            logger_saga.info(f"Локальная бд упала при сохранении: {e}")
            await self.market_data_client.delete_additional_info(exchange_name=exchange_dict['exchange_name'])
            logger_saga.info("Мусор во 2 сервисе удален")

            raise LocalDBError(object_type="Exchange", object_name=exchange_dict['exchange_name'])


        try:
            exchanges_cache = await self.redis.get(exchange_key)
            if exchanges_cache:
                exchanges_list = ujson.loads(exchanges_cache)
                new_exchange_schema = ExchangeResponseSchema.model_validate(exchange)
                new_exchange_dict = new_exchange_schema.model_dump(mode='json')

                exchanges_list.append(new_exchange_dict)

                await self.redis.set(exchange_key, ujson.dumps(exchanges_list), ex=3600)
                logger_saga.info("Новая биржа добавлена в кэш")

        except Exception as e:
            logger_saga.error(f"кэш в саге не обновился из-за ошибки: {e}")
            await self.redis.delete(exchange_key)

        logger_saga.info(f"сага завершена, у биржи {exchange_dict['exchange_name']} статус - FINISHED")


        return ExchangeResponseSchema.model_validate(exchange)
