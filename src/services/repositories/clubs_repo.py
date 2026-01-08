from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.services.exceptions import NothingExists
from src.services.repositories.ready_info import ReadyInfoForAddRepo
from src.services.schemas.schemas import PlayerSchemaUpdate, PlayerSchema
from src.services.schemas.schemas import ClubSchemaUpdate
from src.models.football_players import Player
from src.services.schemas.schemas import ClubSchema
from src.models.clubs import Club



class ClubFootballersRepository:
    @classmethod
    async def add_club(cls, club_data: ClubSchema, db_session: AsyncSession):
        club, players = ReadyInfoForAddRepo.get_club_and_players(club_data)
        club.players = players

        db_session.add(club)
        db_session.add_all(players)
        await db_session.flush()
        await db_session.refresh(club)

        return ClubSchema.model_validate(club_data)


    @classmethod
    async def get_clubs_info(cls, db_session: AsyncSession):
        result = await db_session.execute(select(Club).options(selectinload(Club.players))) #сразу загрузка и игроков
        clubs_models = result.scalars().all()
        clubs_schemas = [ClubSchema.model_validate(club) for club in clubs_models]
        return clubs_schemas


    @classmethod
    async def update_clubs_info(cls, update_sch: ClubSchemaUpdate, db_session: AsyncSession):
        update_sch_dict = update_sch.model_dump(exclude_none=True)
        query = select(Club).where(Club.id == update_sch.id).options(selectinload(Club.players))
        result = await db_session.execute(query)
        existing_club = result.scalar_one_or_none()

        for key, value in update_sch_dict.items():
            if hasattr(existing_club, key):
                setattr(existing_club, key, value)

        await db_session.flush()
        await db_session.refresh(existing_club)

        return ClubSchema.model_validate(existing_club)


    @classmethod
    async def update_players_info(cls, update_player_sch: PlayerSchemaUpdate, db_session: AsyncSession):
        update_sch_dict = update_player_sch.model_dump(exclude_none=True)
        query = select(Player).where(Player.id == update_player_sch.id)
        result_player = await db_session.execute(query)
        existing_player = result_player.scalar_one_or_none()

        for key, value in update_sch_dict.items():
            if hasattr(existing_player, key):
                setattr(existing_player, key, value)

        await db_session.flush()
        await db_session.refresh(existing_player)

        return PlayerSchema.model_validate(existing_player)


    @classmethod
    async def delete_club_or_player(cls, delete_id, db_session: AsyncSession):
        club_by_id = await db_session.get(Club, delete_id)
        if club_by_id is not None:
            await db_session.delete(club_by_id)
            return club_by_id

        player = await db_session.get(Player, delete_id)
        if player is not None:
            await db_session.delete(player)
            return player

        else:
            raise NothingExists(delete_id)
