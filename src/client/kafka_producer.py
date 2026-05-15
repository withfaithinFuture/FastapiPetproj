import asyncio
import logging
from typing import Dict, List
import ujson
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
from src.core.exceptions import ClientNotStartedError


logger = logging.getLogger('workers.kafka_producer')


class KafkaProducerClient:

    def __init__(self, servers: str):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=servers,
            value_serializer=self.serializer,
            acks='all',
            enable_idempotence=True,
        )
        self.is_started = False
        self.lock = asyncio.Lock()


    @staticmethod
    def serializer(data: Dict | List | str) -> bytes:
        if isinstance(data, (dict, list)):
            return ujson.dumps(data).encode('utf-8')
        return str(data).encode('utf-8')


    async def start(self) -> None:
        async with self.lock:
            if self.is_started:
                logger.warning("Producer из MVC-сервиса уже запущен")
                return

            logger.info("Producer из MVC-сервиса начал работу")
            await self.producer.start()
            self.is_started = True


    async def stop(self) -> None:
        async with self.lock:
            if not self.is_started:
                logger.warning("Producer из MVC-сервиса уже остановлен")
                return

            logger.info("Producer из MVC-сервиса закончил работу")
            await self.producer.stop()
            self.is_started = False


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(1, max=5),
        retry=retry_if_exception_type(KafkaError),
        reraise=True
    )
    async def send_message(self, topic: str, payload: Dict | List | str) -> None:
        if not self.is_started:
            raise ClientNotStartedError(client_name='Kafka_producer')

        logger.info(f"Producer из MVC-сервиса отправил сообщениие: topic - {topic}")
        await self.producer.send_and_wait(topic=topic, value=payload)