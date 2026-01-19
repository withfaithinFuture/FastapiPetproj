import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.core.exceptions import NotFoundError
from src.models.shares import Share
from src.models.users import User
from src.services.repositories.shares_repo import UserSharesRepository as user_rep
from src.services.schemas.shares_schemas import UserSchema, UserSchemaUpdate, SharesSchemaUpdate


logger_shares = logging.getLogger("services.shares")

class SharesService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_rep = user_rep(self.session)



    async def add_shares_service(self, user_data: UserSchema) -> UserSchema:
        logger_shares.info("Добавление   пользователя с акциями")
        user_data_dict = user_data.model_dump(exclude='user_shares')
        new_user = User(**user_data_dict)

        shares = []
        for share in user_data.user_shares:
            share_data_dict = share.model_dump()
            new_share = Share(**share_data_dict)
            shares.append(new_share)

        logger_shares.info(f"Создано акций: {len(shares)}")
        new_user.user_shares = shares

        saved_user = await self.user_rep.add_shares(new_user, shares)
        logger_shares.info(f"Пользователь сохранен: username={saved_user.username}, ID={saved_user.id}")

        return UserSchema.model_validate(saved_user)


    async def get_shares_info_service(self) -> list[Share]:
        logger_shares.info("Запрос информации об акциях")
        result_scalar = await self.user_rep.get_shares_info()
        logger_shares.info(f"Получено записей: {len(result_scalar)}")
        return result_scalar


    async def update_user_shares_info_service(self, user_id: UUID, update_data: UserSchemaUpdate) -> UserSchemaUpdate:
        logger_shares.info(f"Обновление пользователя: ID={user_id}")

        update_data_dict = update_data.model_dump(exclude_none=True)
        existing_user = await self.user_rep.get_user_by_id(user_id)

        if existing_user is None:
            logger_shares.warning(f"Пользователь не найден: ID={user_id}")
            raise NotFoundError(user_id, 'user')

        for key, value in update_data_dict.items():
            if hasattr(existing_user, key):
                setattr(existing_user, key, value)

        await self.user_rep.update_object(existing_user)
        logger_shares.info(f"Пользователь обновлен: ID={user_id}")

        return UserSchemaUpdate.model_validate(existing_user)


    async def update_share_info_service(self, share_id: UUID, update_info: SharesSchemaUpdate) -> SharesSchemaUpdate:
        logger_shares.info(f"Обновление акции: ID={share_id}")

        update_info_dict = update_info.model_dump(exclude_none=True)
        existing_share = await self.user_rep.get_share_by_id(share_id)

        if existing_share is None:
            logger_shares.warning(f"Акция не найдена: ID={share_id}")
            raise NotFoundError(share_id, 'share')

        for key, value in update_info_dict.items():
            if hasattr(existing_share, key):
                setattr(existing_share, key, value)

        await self.user_rep.update_object(existing_share)
        logger_shares.info(f"Акция обновлена: ID={share_id}")

        return SharesSchemaUpdate.model_validate(existing_share)


    async def delete_owner_or_share(self, delete_id: UUID) -> User | Share:
        logger_shares.info(f"Удаление объекта: ID={delete_id}")

        existing_user, existing_share = await self.user_rep.get_shares_or_user_by_id(delete_id)

        if existing_user is not None:
            logger_shares.info(f"Найден пользователь для удаления: ID={delete_id}")
            await self.user_rep.delete_owner_or_share(existing_user)
            logger_shares.info(f"Пользователь удален: ID={delete_id}")
            return existing_user

        if existing_share is not None:
            logger_shares.info(f"Найдена акция для удаления: ID={delete_id}")
            await self.user_rep.delete_owner_or_share(existing_share)
            logger_shares.info(f"Акция удалена: ID={delete_id}")
            return existing_share

        else:
            logger_shares.warning(f"Объект не найден: ID={delete_id}")
            raise NotFoundError(delete_id, 'user_or_share')