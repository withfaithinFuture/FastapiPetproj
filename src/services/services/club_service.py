import json
import logging
from uuid import UUID
import ujson
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, wait_exponential_jitter, stop_after_attempt, retry_if_exception, retry_if_exception_type
from src.services.core.exceptions import CacheNotSavedError
from src.services.core.exceptions import NotFoundError
from src.services.schemas.player_schemas import PlayerSchemaUpdate
from src.models.football_players import Player
from src.models.clubs import Club
from src.services.schemas.club_schemas import ClubSchema, ClubSchemaUpdate, PlayerSchema
from src.services.repositories.clubs_repo import ClubFootballersRepository as club_rep
from redis.exceptions import ConnectionError, TimeoutError, RedisError


logger_club = logging.getLogger('services.clubs')


class ClubService:

    def __init__(self, session: AsyncSession, redis: Redis, clubs_key = "clubs:all"):
        self.session = session
        self.club_rep = club_rep(self.session)
        self.redis = redis
        self.clubs_key = clubs_key

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(1, max=3),
        retry=retry_if_exception_type((CacheNotSavedError, ConnectionError, TimeoutError)),
        reraise=True
    )
    async def set_cache_retry(self, key: str, value: str, expire: int):
        await self.redis.set(key=key, value=value, ex=expire)
        saved_cache_check = await self.redis.exists(key)
        if not saved_cache_check:
            logger_club.warning(f"Данные с ключом {key} не сохранились")
            raise CacheNotSavedError()

        logger_club.info("Данные занесены в кеш после ретраев")


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
        new_club_schema = ClubSchema.model_validate(new_club)

        try:
            cached_data = await self.redis.get(self.clubs_key)
            if cached_data:
                clubs_data = ujson.loads(cached_data)
                clubs_data.append(new_club_schema.model_dump(mode='json'))
                json_data = ujson.dumps(clubs_data)

                await self.set_cache_retry(key=self.clubs_key, value=json_data, expire=3600)
                logger_club.info("Новый клуб добавлен в имеющийся кэш")

        except Exception as e:
            logger_club.error(f"Не удалось обновить данные в Redis: {e}")
            await self.redis.delete(self.clubs_key)

        logger_club.info(f"Клуб добавлен: name={new_club.name}")

        return new_club_schema


    async def get_clubs_info_service(self) -> list[ClubSchema]:
        logger_club.info("Запрос информации о клубах")

        cached_data = await self.redis.get(self.clubs_key)
        if cached_data:
            logger_club.info("Данные о клубах получены из redis-кеша")
            clubs_data = ujson.loads(cached_data)
            return [ClubSchema.model_validate(club) for club in clubs_data]

        clubs_models = await self.club_rep.get_clubs_info()
        clubs_schemas = [ClubSchema.model_validate(club) for club in clubs_models]
        clubs_list = [club.model_dump(mode='json') for club in clubs_schemas]
        json_data = ujson.dumps(clubs_list)
        await self.set_cache_retry(self.clubs_key, json_data, 3600)
        logger_club.info(f"Получено клубов: {len(clubs_schemas)}")
        return clubs_schemas


    async def update_clubs_info_service(self, club_id: UUID, update_sch: ClubSchemaUpdate) -> ClubSchema | None:
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

        try:
            cached_data = await self.redis.get(self.clubs_key)
            if cached_data:
                clubs = ujson.loads(cached_data)

                for i, club_data in enumerate(clubs):
                    if club_data.get('id') == str(club_id):
                        clubs[i].update(update_sch_dict)
                        break

                await self.set_cache_retry(key=self.clubs_key, value=json.dumps(clubs, default=str), expire=3600)
                logger_club.info(f"Кэш клубов успешно обновлен")

        except Exception as e:
            logger_club.error(f"Не удалось обновить данные в Redis: {e}")
            await self.redis.delete(self.clubs_key)

        logger_club.info(f"Клуб обновлен: ID={club_id}")

        return ClubSchema.model_validate(existing_club)


    async def update_players_info_service(self, player_id: UUID, update_player_sch: PlayerSchemaUpdate) -> PlayerSchema | None:
        logger_club.info(f"Обновление игрока: ID={player_id}")

        update_sch_dict = update_player_sch.model_dump(exclude_none=True)
        existing_player = await self.club_rep.get_player_by_id(player_id)

        if existing_player is None:
            logger_club.warning(f"Игрок не найден: ID={player_id}")
            raise NotFoundError(player_id, "Player")

        for key, value in update_sch_dict.items():
            if hasattr(existing_player, key):
                setattr(existing_player, key, value)

        await self.club_rep.update_info(existing_player)

        try:
            cached_data = self.redis.get(self.clubs_key)
            if cached_data:
                clubs_data = ujson.loads(cached_data)
                updated = False

                for club in clubs_data:
                    players = club.get('players', [])
                    for i, players in enumerate(players):
                        if players.get('id') == str(player_id):
                            players[i].update(update_sch_dict)
                            updated = True
                            break

                    if updated:
                        break

                if updated:
                    json_data = ujson.dumps(clubs_data)
                    await self.set_cache_retry(key=self.clubs_key, value=json_data, expire=3600)
                    logger_club.info("Данные игрока обновлены в кэше")

                else:
                    await self.redis.delete(self.clubs_key)

        except Exception as e:
            await self.redis.delete(self.clubs_key)

        logger_club.info(f"Игрок обновлен: ID={player_id}")

        return PlayerSchema.model_validate(existing_player)



    async def delete_club_by_id(self, club_id: UUID):
        logger_club.info(f"Удаление клуба: ID={club_id}")
        club_by_id = await self.club_rep.get_club_with_players(club_id)

        if club_by_id is None:
            logger_club.warning(f"Клуб не найден: ID={club_id}")
            raise NotFoundError(club_id, 'Club')

        logger_club.info(f"Найден клуб для удаления: ID={club_id}")
        await self.club_rep.delete_club_or_player(club_by_id)
        await self.redis.delete(self.clubs_key)
        logger_club.info(f"Клуб удален: ID={club_id}")

        return True


    async def delete_player_by_id(self, player_id: UUID):
        logger_club.info(f"Удаление футболиста: ID={player_id}")
        player_by_id = await self.club_rep.get_player_by_id(player_id)

        if player_by_id is None:
            logger_club.warning(f"Футболист не найден: ID={player_id}")
            raise NotFoundError(player_id, 'Player')

        logger_club.info(f"Найден игрок для удаления: ID={player_id}")
        await self.club_rep.delete_club_or_player(player_by_id)
        await self.redis.delete(self.clubs_key)
        logger_club.info(f"Игрок удален: ID={player_id}")

        return True