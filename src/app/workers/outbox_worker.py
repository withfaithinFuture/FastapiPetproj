import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.sql import func
from sqlalchemy import select, update
from src.schemas.outbox_schemas import OutboxDLQPayloadSchema
from src.app.config import settings
from src.enums.outbox_enums import OutboxStatus
from src.models.outbox import OutboxEvent
from src.client.kafka_producer import KafkaProducerClient
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
                logger.error(f"Ошибка в outbox_worker в методе run: {e}")
                await asyncio.sleep(interval_sec)


    async def run_recovery(self, interval_sec: float) -> None:
        while True:
            try:
                await self.recover_in_progress_messages()
                await asyncio.sleep(interval_sec)

            except Exception as e:
                logger.error(f"Ошибка в outbox_worker в методе run_recovery: {e}")
                await asyncio.sleep(interval_sec)


    async def process_message(self, batch_size: int) -> None:
        dlq_topic = settings.dlq_topic
        max_attempts = 3

        async with new_session() as session:
            query_pending = (
                select(OutboxEvent.id)
                .where(OutboxEvent.status == OutboxStatus.PENDING)
                .limit(batch_size)
                .with_for_update(skip_locked=True)
            )

            query_update = (
                update(OutboxEvent)
                .where(OutboxEvent.id.in_(query_pending))
                .values(status=OutboxStatus.IN_PROGRESS, fix_attempts=OutboxEvent.fix_attempts + 1)
                .returning(OutboxEvent.id, OutboxEvent.topic, OutboxEvent.payload, OutboxEvent.fix_attempts, OutboxEvent.created_at)
            )

            result = await session.execute(query_update)
            events = result.mappings().all()
            await session.commit()

            if not events:
                return

        successful_ids = []
        retry_ids = []
        failed_ids = []

        for event in events:
            try:
                await self.kafka_client.send_message(topic=event['topic'], payload=event['payload'])
                successful_ids.append(event['id'])
                logger.info(f"Отправлено сообщение {event['id']} в Кафку")

            except Exception as send_error:
                logger.error(f"Ошибка при отправке сообщения (id={event['id']}): {send_error}")

                if event['fix_attempts'] < max_attempts:
                    retry_ids.append(event['id'])

                else:
                    dlq_payload = OutboxDLQPayloadSchema(event_id=str(event['id']), original_topic=event['topic'], failed_payload=event['payload'], error_message=str(send_error), created_at=event['created_at'], retry_count=event['fix_attempts'])
                    try:
                        await self.kafka_client.send_message(topic=dlq_topic, payload=dlq_payload.model_dump(mode='json'))
                        failed_ids.append(event['id'])

                    except Exception as dlq_error:
                        logger.error(f"Не удалось отправить в DLQ: {dlq_error}")
                        retry_ids.append(event['id'])


        if successful_ids or retry_ids or failed_ids:
            async with new_session() as session:
                if successful_ids:
                    query_successful = (
                        update(OutboxEvent)
                        .where(OutboxEvent.id.in_(successful_ids))
                        .values(status=OutboxStatus.SENT)
                    )
                    await session.execute(query_successful)

                if retry_ids:
                    query_retry = (
                        update(OutboxEvent)
                        .where(OutboxEvent.id.in_(retry_ids))
                        .values(status=OutboxStatus.PENDING)
                    )
                    await session.execute(query_retry)

                if failed_ids:
                    query_failed = (
                        update(OutboxEvent)
                        .where(OutboxEvent.id.in_(failed_ids))
                        .values(status=OutboxStatus.FAILED)
                    )
                    await session.execute(query_failed)

                await session.commit()
                logger.info(f"Закоммичено {len(successful_ids)} успешных ивентов, неудачных - {len(failed_ids)}. Отправлено на ретрай - {len(retry_ids)}")


    async def recover_in_progress_messages(self, timeout_sec: int = 200) -> None:
        update_delta = datetime.now() - timedelta(seconds=timeout_sec)

        async with new_session() as session:
            query = (
                update(OutboxEvent)
                .where(OutboxEvent.status == OutboxStatus.IN_PROGRESS, OutboxEvent.updated_at <= update_delta)
                .values(status=OutboxStatus.PENDING, updated_at=func.now())

            )
            result = await session.execute(query)
            await session.commit()

            if result.rowcount > 0:
                logger.info(f"Было восстановлено {result.rowcount} застрявших ивентов")