import logging
import ujson
from aiokafka import AIOKafkaProducer


logger = logging.getLogger('workers.kafka_producer')


class KafkaProducerClient:

    def __init__(self, servers: str):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=servers,
            value_serializer=self.serializer,
            acks='all',
            enable_idempotence=True
        )


    @staticmethod
    def serializer(data: str) -> bytes:
        if isinstance(data, (dict, list)):
            return ujson.dumps(data).encode('utf-8')
        return str(data).encode('utf-8')


    async def start(self):
        logger.info("Producer из MVC-сервиса начал работу")
        await self.producer.start()


    async def stop(self):
        logger.info("Producer из MVC-сервиса закончил работу")
        await self.producer.stop()


    async def send_message(self, topic: str, payload: dict):
        logger.info(f"Producer из MVC-сервиса отправил сообщениие: topic - {topic}, \n payload - {payload}")
        await self.producer.send_and_wait(topic=topic, value=payload)