from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.shares import Share
from src.models.users import User
from src.models.exchange_owners import Owner
from src.models.exchanges import Exchange
from src.services.exceptions import ValidationError
from src.models.football_players import Player
from src.models.clubs import Club
from src.services.schemas.schemas import ClubSchemaUpdate, PlayerSchemaUpdate, ExchangeUpdateSchema, \
    ExchangeOwnerUpdateSchema, SharesSchemaUpdate, UserSchemaUpdate


async def validate_exist_club(data: ClubSchemaUpdate, session: AsyncSession):
    club = data.model_dump()
    club_id = club.get("id")
    query = select(Club).where(Club.id == club_id)
    result = await session.execute(query)
    existing_club = result.scalar_one_or_none()

    if not existing_club:
        raise ValidationError(club_id)

    return data


async def validate_exist_player(data: PlayerSchemaUpdate, session: AsyncSession):
    player = data.model_dump()
    player_id = player.get("id")
    query = select(Player).where(Player.id == player_id)
    result = await session.execute(query)
    existing_player = result.scalar_one_or_none()

    if not existing_player:
        raise ValidationError(player_id, f"Футболист с ID = {player_id} не найден! Введите корректный ID!")

    return data


async def validate_exchange_exist(data: ExchangeUpdateSchema, db_session: AsyncSession):
    update_data = data.model_dump()
    query = select(Exchange).where(Exchange.id == update_data['id'])
    result = await db_session.execute(query)
    exist_object = result.scalar_one_or_none()

    if exist_object is None:
        raise ValidationError(update_data['id'], f"Биржи с таким ID = {update_data['id']} не существует! Введите корректный ID!")


async def validate_owner_exist(data: ExchangeOwnerUpdateSchema, db_session: AsyncSession):
    data_dict = data.model_dump()
    query = select(Owner).where(Owner.id == data_dict['id'])
    result = await db_session.execute(query)
    exist_owner = result.scalar_one_or_none()

    if exist_owner is None:
        raise ValidationError(data_dict['id'], f"Создателя биржи с таким ID = {data_dict['id']} не существует! Введите корректный ID!")


async def validate_user_exist(data: UserSchemaUpdate, db_session: AsyncSession):
    data_dict = data.model_dump()
    query = select(Owner).where(User.id == data_dict['id'])
    result = await db_session.execute(query)
    exist_user = result.scalar_one_or_none()

    if exist_user is None:
        raise ValidationError(data_dict['id'], f"Юзера с ID = {data_dict['id']} не существует! Введите корректный ID!")


async def validate_share_exist(data: SharesSchemaUpdate, db_session: AsyncSession):
    data_dict = data.model_dump()
    query = select(Share).where(Share.id == data_dict['id'])
    result = await db_session.execute(query)
    exist_share = result.scalar_one_or_none()

    if exist_share is None:
        raise ValidationError(data_dict['id'], f"Акция с ID = {data_dict['id']} не существует! Введите корректный ID!")