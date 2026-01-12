from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.core.exceptions import NothingExists, ValidationError
from src.models.shares import Share
from src.models.users import User
from src.services.repositories.shares_repo import UserSharesRepository as UsRep
from src.services.schemas.shares_schemas import UserSchema, UserSchemaUpdate, SharesSchemaUpdate


class SharesService:
    @classmethod
    async def add_shares_service(cls, user_data: UserSchema, db_session: AsyncSession):
        user_data_dict = user_data.model_dump(exclude='user_shares')
        new_user = User(**user_data_dict)

        shares = []
        for share in user_data.user_shares:
            share_data_dict = share.model_dump()
            new_share = Share(**share_data_dict)
            shares.append(new_share)

        new_user.user_shares = shares

        saved_user = await UsRep.add_shares(new_user, shares, db_session)
        return UserSchema.model_validate(saved_user)


    @classmethod
    async def get_shares_info_service(cls, db_session: AsyncSession):
        result_scalar = await UsRep.get_shares_info(db_session)
        return result_scalar


    @classmethod
    async def update_user_shares_info_service(cls, user_id: UUID, update_data: UserSchemaUpdate, db_session: AsyncSession):
        update_data_dict = update_data.model_dump(exclude_none=True)
        existing_user = await UsRep.get_user_by_id(user_id, db_session)

        if existing_user is None:
            raise ValidationError(user_id, f"Юзера с ID = {user_id} не существует! Введите корректный ID!")

        for key, value in update_data_dict.items():
            if hasattr(existing_user, key):
                setattr(existing_user, key, value)

        await UsRep.update_object(existing_user, db_session)
        return UserSchemaUpdate.model_validate(existing_user)


    @classmethod
    async def update_share_info_service(cls, share_id: UUID, update_info: SharesSchemaUpdate, db_session: AsyncSession):
        update_info_dict = update_info.model_dump(exclude_none=True)
        existing_share = await UsRep.get_share_by_id(share_id, db_session)

        if existing_share is None:
            raise ValidationError(share_id, f"Акция с ID = {share_id} не существует! Введите корректный ID!")

        for key, value in update_info_dict.items():
            if hasattr(existing_share, key):
                setattr(existing_share, key, value)

        await UsRep.update_object(existing_share, db_session)
        return SharesSchemaUpdate.model_validate(existing_share)


    @classmethod
    async def delete_owner_or_share(cls, delete_id: UUID, db_session: AsyncSession):
        existing_user, existing_share = await UsRep.get_shares_or_user_by_id(delete_id, db_session)

        if existing_user is not None:
            await UsRep.delete_owner_or_share(existing_user, db_session)
            return existing_user

        if existing_share is not None:
            await UsRep.delete_owner_or_share(existing_share, db_session)
            return existing_share

        else:
            raise NothingExists(delete_id, f"Акций или юзера с ID = {delete_id} не существует! Введите корректный ID!")