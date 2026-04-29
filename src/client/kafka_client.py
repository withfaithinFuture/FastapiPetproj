import logging
from typing import Dict
import ujson
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
from src.core.exceptions import RunTimeError


logger = logging.getLogger('workers.kafka_producer')


class KafkaProducerClient:

    def __init__(self, servers: str):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=servers,
            value_serializer=self.serializer,
            acks='all',
            enable_idempotence=True,
            transactional_id='outbox_producer1'
        )
        self.is_started = False


    @staticmethod
    def serializer(data: str) -> bytes:
        if isinstance(data, (dict, list)):
            return ujson.dumps(data).encode('utf-8')
        return str(data).encode('utf-8')


    async def start(self) -> None:
        if self.is_started:
            logger.warning("Producer из MVC-сервиса уже запущен")
            return

        logger.info("Producer из MVC-сервиса начал работу")
        await self.producer.start()
        self.is_started = True


    async def stop(self) -> None:
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
    async def send_message(self, topic: str, payload: Dict) -> None:
        if not self.is_started:
            raise RunTimeError(client_name='Kafka_producer')

        logger.info(f"Producer из MVC-сервиса отправил сообщениие: topic - {topic}, \n payload - {payload}")
        await self.producer.send_and_wait(topic=topic, value=payload)