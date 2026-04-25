import json
import logging
import uuid
from typing import List, Optional
from uuid import UUID
import ujson
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.enums.outbox_enums import OutboxStatus
from src.app.config import settings
from src.models.outbox import OutboxEvent
from src.core.exceptions import NotFoundError, NameDuplicateError
from src.schemas.shares_schemas import SharesSchemaUpdate, SharesSchema
from src.schemas.shares_users_schemas import UserSchema, UserSchemaUpdate, UserSharesFastResponseSchema
from src.models.shares import Share
from src.models.users import User
from src.repositories.shares_repo import UserSharesRepository as user_rep


logger_shares = logging.getLogger("services.shares")


class SharesService:

    def __init__(self, session: AsyncSession, redis: Redis, shares_key: str = "shares:all"):
        self.session = session
        self.user_rep = user_rep(self.session)
        self.redis = redis
        self.shares_key = shares_key


    async def create_shares_service(self, user_data: UserSchema) -> UserSharesFastResponseSchema:
        logger_shares.info("Добавление пользователя с акциями")
        user_data_dict = user_data.model_dump(exclude='user_shares')

        username = user_data_dict.get('username')
        existing_user = await self.user_rep.get_user_by_username(username=user_data_dict.get('username'))
        if existing_user:
            logger_shares.info(f"Пользователь с username = {username} уже существует в БД, введите другой username")
            raise NameDuplicateError(object_name=username, object_type='User')

        new_user = User(**user_data_dict)
        shares = []

        for share in user_data.user_shares:
            share_data_dict = share.model_dump()
            new_share = Share(**share_data_dict)
            shares.append(new_share)

        logger_shares.info(f"Создано акций: {len(shares)}")
        new_user.user_shares = shares

        event_id = uuid.uuid4()
        outbox_payload = {
            "event_id": str(event_id),
            "action": "ENRICH_USER_SHARES_DATA",
            "username": username,
            "email": user_data_dict.get('email'),
            "shares_broker": user_data_dict.get('shares_broker')
        }

        outbox_event = OutboxEvent(
            id=event_id,
            topic=settings.topic_enrich_name,
            payload=outbox_payload,
            status=OutboxStatus.PENDING
        )

        saved_user = await self.user_rep.create_shares(new_user, shares)
        self.session.add(outbox_event)
        await self.session.commit()
        logger_shares.info(f"Заявка {username} и outbox успешно сохранены в бд")

        try:
            cached_data = await self.redis.get(self.shares_key)
            if cached_data:
                users_list = ujson.loads(cached_data)
                new_user_dict = UserSchema.model_validate(saved_user).model_dump(mode='json')
                users_list.append(new_user_dict)

                await self.redis.set(self.shares_key, ujson.dumps(users_list), ex=3600)
                logger_shares.info(f"Новый пользователь {saved_user.username} добавлен в кэш")

        except Exception as e:
            logger_shares.error(f"Ошибка добавления в кэш: {e}")
            await self.redis.delete(self.shares_key)

        return UserSharesFastResponseSchema(username=username, user_shares=[SharesSchema.model_validate(share) for share in shares])


    async def get_shares_info_service(self) -> List[UserSchema]:
        logger_shares.info("Запрос информации об акциях")

        cashed_data = await self.redis.get(self.shares_key)
        if cashed_data:
            logger_shares.info("Данные акций получены из Redis")
            user_data = json.loads(cashed_data)
            return [UserSchema.model_validate(user) for user in user_data]

        users_models = await self.user_rep.get_shares_info()
        users_schemas = [UserSchema.model_validate(user) for user in users_models]

        shares_data = [schema.model_dump() for schema in users_schemas]
        json_data = json.dumps(shares_data, default=str)
        await self.redis.set(self.shares_key, json_data, ex=3600)
        logger_shares.info(f"Получено записей: {len(users_schemas)}")
        return users_schemas


    async def update_user_shares_info_service(self, user_id: UUID, update_data: UserSchemaUpdate) -> Optional[UserSchemaUpdate]:
        logger_shares.info(f"Обновление пользователя: ID={user_id}")

        update_data_dict = update_data.model_dump(exclude_none=True, mode='json')
        existing_user = await self.user_rep.get_user_by_id(user_id)

        if existing_user is None:
            logger_shares.warning(f"Пользователь не найден: ID={user_id}")
            raise NotFoundError(user_id, 'user')

        for key, value in update_data_dict.items():
            if hasattr(existing_user, key):
                setattr(existing_user, key, value)

        await self.user_rep.update_object(existing_user)

        try:
            cached_data = await self.redis.get(self.shares_key)
            if cached_data:
                users_list = ujson.loads(cached_data)
                for user in users_list:
                    if str(user.get('id')) == str(user_id):
                        user.update(update_data_dict)
                        break

                await self.redis.set(self.shares_key, ujson.dumps(users_list), ex=3600)
                logger_shares.info(f"Кэш пользователя {existing_user.username} обновлен")

        except Exception as e:
            logger_shares.error(f"Ошибка при обновлении кэша пользователя: {e}")
            await self.redis.delete(self.shares_key)

        logger_shares.info(f"Пользователь обновлен: ID={user_id}")
        return UserSchemaUpdate.model_validate(existing_user)


    async def update_share_info_service(self, share_id: UUID, update_info: SharesSchemaUpdate) -> Optional[SharesSchemaUpdate]:
        logger_shares.info(f"Обновление акции: ID={share_id}")

        update_info_dict = update_info.model_dump(exclude_none=True, mode='json')
        existing_share = await self.user_rep.get_share_by_id(share_id)

        if existing_share is None:
            logger_shares.warning(f"Акция не найдена: ID={share_id}")
            raise NotFoundError(share_id, 'share')

        for key, value in update_info_dict.items():
            if hasattr(existing_share, key):
                setattr(existing_share, key, value)

        await self.user_rep.update_object(existing_share)

        try:
            cached_data = await self.redis.get(self.shares_key)
            if cached_data:
                users_list = ujson.loads(cached_data)
                updated = False

                for user in users_list:
                    for share in user.get('user_shares', []):
                        if str(share.get('id')) == str(share_id):
                            share.update(update_info_dict)
                            updated = True
                            break

                    if updated:
                        break

                await self.redis.set(self.shares_key, ujson.dumps(users_list), ex=3600)
                logger_shares.info("Кэш акции обновлен")

        except Exception as e:
            logger_shares.error(f"Ошибка при обновлении кэша акции: {e}")
            await self.redis.delete(self.shares_key)

        logger_shares.info(f"Акция обновлена: ID={share_id}")
        return SharesSchemaUpdate.model_validate(existing_share)


    async def delete_user_by_id(self, owner_id: UUID) -> bool:
        logger_shares.info(f"Удаление владельца акций: ID={owner_id}")
        owner_by_id = await self.user_rep.get_user_by_id(owner_id)

        if owner_by_id is None:
            logger_shares.warning(f"Владелец акций не найден: ID={owner_id}")
            raise NotFoundError(owner_id, 'User')

        logger_shares.info(f"Найден владелец акций для удаления: ID={owner_id}")
        await self.user_rep.delete_user_or_share(owner_by_id)
        await self.redis.delete(self.shares_key)
        logger_shares.info(f"Владелец акций удален: ID={owner_id}")

        return True


    async def delete_share_by_id(self, share_id: UUID) -> bool:
        logger_shares.info(f"Удаление акции: ID={share_id}")
        share_by_id = await self.user_rep.get_share_by_id(share_id)

        if share_by_id is None:
            logger_shares.warning(f"Акция не найдена: ID={share_id}")
            raise NotFoundError(share_id, 'Share')

        logger_shares.info(f"Найдена акция для удаления: ID={share_id}")
        await self.user_rep.delete_user_or_share(share_by_id)
        await self.redis.delete(self.shares_key)
        logger_shares.info(f"Акция удалена: ID={share_id}")

        return True

