import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.core.exceptions import NotFoundError
from src.models.football_players import Player
from src.models.clubs import Club
from src.services.schemas.club_schemas import ClubSchema, ClubSchemaUpdate, PlayerSchemaUpdate, PlayerSchema
from src.services.repositories.clubs_repo import ClubFootballersRepository as club_rep


logger_club = logging.getLogger('services.clubs')


class ClubService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.club_rep = club_rep(self.session)


    async def create_club_service(self, club_data: ClubSchema) -> ClubSchema:
        logger_club.info("Добавление клуба с игроками")

        club_data_dict = club_data.model_dump(exclude='players')
        new_club = Club(**club_data_dict)

        players = []
        for player in club_data.players:
            player_data_dict = player.model_dump()
            new_player = Player(**player_data_dict)
            players.append(new_player)

        logger_club.info(f"Создано игроков: {len(players)}")
        new_club.players = players
        await self.club_rep.create_club(new_club, players)
        logger_club.info(f"Клуб добавлен: name={new_club.name}")

        return ClubSchema.model_validate(new_club)


    async def get_clubs_info_service(self) -> list[ClubSchema]:
        logger_club.info("Запрос информации о клубах")
        clubs_models = await self.club_rep.get_clubs_info()
        clubs_schemas = [ClubSchema.model_validate(club) for club in clubs_models]
        logger_club.info(f"Получено клубов: {len(clubs_schemas)}")
        return clubs_schemas


    async def update_clubs_info_service(self, club_id: UUID, update_sch: ClubSchemaUpdate) -> ClubSchema:
        logger_club.info(f"Обновление клуба: ID={club_id}")

        update_sch_dict = update_sch.model_dump(exclude_none=True)
        existing_club = await self.club_rep.get_club_with_players(club_id)

        if existing_club is None:
            logger_club.warning(f"Клуб не найден: ID={club_id}")
            raise NotFoundError(club_id, 'club')

        for key, value in update_sch_dict.items():
            if hasattr(existing_club, key):
                setattr(existing_club, key, value)

        await self.club_rep.update_info(existing_club)
        logger_club.info(f"Клуб обновлен: ID={club_id}")

        return ClubSchema.model_validate(existing_club)


    async def update_players_info_service(self, player_id: UUID, update_player_sch: PlayerSchemaUpdate) -> PlayerSchema:
        logger_club.info(f"Обновление игрока: ID={player_id}")

        update_sch_dict = update_player_sch.model_dump(exclude_none=True)
        existing_player = await self.club_rep.get_player_by_id(player_id)

        if existing_player is None:
            logger_club.warning(f"Игрок не найден: ID={player_id}")
            raise NotFoundError(player_id, "player")

        for key, value in update_sch_dict.items():
            if hasattr(existing_player, key):
                setattr(existing_player, key, value)

        await self.club_rep.update_info(existing_player)
        logger_club.info(f"Игрок обновлен: ID={player_id}")

        return PlayerSchema.model_validate(existing_player)


    async def delete_club_or_player(self, delete_id: UUID) -> Club | Player:
        logger_club.info(f"Удаление объекта: ID={delete_id}")

        club_by_id, player_by_id = await self.club_rep.get_club_or_player_by_id(delete_id)

        if club_by_id is not None:
            logger_club.info(f"Найден клуб для удаления: ID={delete_id}")
            await self.club_rep.delete_club_or_player(club_by_id)
            logger_club.info(f"Клуб удален: ID={delete_id}")
            return club_by_id

        if player_by_id is not None:
            logger_club.info(f"Найден игрок для удаления: ID={delete_id}")
            await self.club_rep.delete_club_or_player(player_by_id)
            logger_club.info(f"Игрок удален: ID={delete_id}")
            return player_by_id

        else:
            logger_club.warning(f"Объект не найден: ID={delete_id} (ни клуб, ни игрок)")
            raise NotFoundError(delete_id, "club_or_player")
