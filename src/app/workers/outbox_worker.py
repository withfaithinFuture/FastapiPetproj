import asyncio
import logging
from sqlalchemy import select
from src.app.config import settings
from src.enums.outbox_enums import OutboxStatus
from src.models.outbox import OutboxEvent
from src.client.kafka_client import KafkaProducerClient
from src.db.db import new_session


logger = logging.getLogger('workers.outbox_worker')


class OutboxWorker:

    def __init__(self, kafka_client: KafkaProducerClient):
        self.kafka_client = kafka_client


    async def run(self, batch_size: int, interval_sec: float) -> None:
        while True:
            try:
                await self.process_message(batch_size=batch_size)
                await asyncio.sleep(interval_sec)

            except Exception as e:
                logger.error(f"Ошибка в outbox_worker: {e}")
                await asyncio.sleep(interval_sec)


    async def process_message(self, batch_size: int) -> None:
        dlq_topic = settings.dlq_topic
        query = (
            select(OutboxEvent)
            .where(OutboxEvent.status == OutboxStatus.PENDING)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )

        async with new_session() as session:
            result = await session.execute(query)
            all_events = result.scalars().all()
            proc_events_cnt = 0

            for event in all_events:
                try:
                    await self.kafka_client.send_message(topic=event.topic, payload=event.payload)
                    event.status = OutboxStatus.SENT
                    proc_events_cnt += 1
                    logger.info(f"Отправлено сообщение {event.id} в Кафку")

                except Exception as send_error:
                    logger.error(f"Ошибка при отправке сообщения (id={event.id}): {send_error}")
                    dlq_payload = {
                    "event_id": str(event.id),
                    "original_topic": event.topic,
                    "failed_payload": event.payload,
                    }

                    try:
                        await self.kafka_client.send_message(topic=dlq_topic, payload=dlq_payload)
                        event.status = OutboxStatus.FAILED

                    except Exception as dlq_error:
                        logger.error(f"Не удалось отправить в DLQ: {dlq_error}")
                        continue

            if all_events:
                try:
                    await session.commit()
                    logger.info(f"Закоммичено {proc_events_cnt} сообщений из {len(all_events)} возможных")

                except Exception as commit_error:
                    await session.rollback()
                    logger.error(f"Ошибка при коммите транзакции: {commit_error}")