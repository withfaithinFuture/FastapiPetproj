from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.core.exceptions import NothingExists, ValidationError
from src.models.football_players import Player
from src.models.clubs import Club
from src.services.schemas.club_schemas import ClubSchema, ClubSchemaUpdate, PlayerSchemaUpdate, PlayerSchema
from src.services.repositories.clubs_repo import ClubFootballersRepository as CLubRep


class ClubService:
    @classmethod
    async def add_club_service(cls, club_data: ClubSchema, db_session: AsyncSession):
        club_data_dict = club_data.model_dump(exclude='players')
        new_club = Club(**club_data_dict)

        players = []
        for player in club_data.players:
            player_data_dict = player.model_dump()
            new_player = Player(**player_data_dict)
            players.append(new_player)

        new_club.players = players
        await CLubRep.add_club(new_club, players, db_session)

        return ClubSchema.model_validate(new_club)


    @classmethod
    async def get_clubs_info_service(cls, db_session: AsyncSession):
        clubs_models = await CLubRep.get_clubs_info(db_session)
        clubs_schemas = [ClubSchema.model_validate(club) for club in clubs_models]
        return clubs_schemas


    @classmethod
    async def update_clubs_info_service(cls, club_id: UUID, update_sch: ClubSchemaUpdate, db_session: AsyncSession):
        update_sch_dict = update_sch.model_dump(exclude_none=True)
        existing_club = await CLubRep.get_club_with_players(club_id, db_session)
        if existing_club is None:
            raise ValidationError(club_id)

        for key, value in update_sch_dict.items():
            if hasattr(existing_club, key):
                setattr(existing_club, key, value)

        await CLubRep.update_info(existing_club, db_session)
        return ClubSchema.model_validate(existing_club)


    @classmethod
    async def update_players_info_service(cls, player_id: UUID, update_player_sch: PlayerSchemaUpdate, db_session: AsyncSession):
        update_sch_dict = update_player_sch.model_dump(exclude_none=True)
        existing_player = await CLubRep.get_player_by_id(player_id, db_session)

        if existing_player is None:
            raise ValidationError(player_id, f"Футболист с ID = {player_id} не найден! Введите корректный ID!")

        for key, value in update_sch_dict.items():
            if hasattr(existing_player, key):
                setattr(existing_player, key, value)

        await CLubRep.update_info(existing_player, db_session)
        return PlayerSchema.model_validate(existing_player)


    @classmethod
    async def delete_club_or_player(cls, delete_id: UUID, db_session: AsyncSession):
        club_by_id, player_by_id = await CLubRep.get_club_or_player_by_id(delete_id, db_session)

        if club_by_id is not None:
            await CLubRep.delete_club_or_player(club_by_id, db_session)
            return club_by_id

        if player_by_id is not None:
            await CLubRep.delete_club_or_player(player_by_id, db_session)
            return player_by_id

        else:
            raise NothingExists(delete_id)