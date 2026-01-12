from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.football_players import Player
from src.models.clubs import Club



class ClubFootballersRepository:
    #взаимодействия только с БД
    @classmethod
    async def add_club(cls, club: Club, players: list[Player],  db_session: AsyncSession):
        db_session.add(club)
        db_session.add_all(players)
        await db_session.flush()
        await db_session.refresh(club)
        return club, players


    @classmethod
    async def get_clubs_info(cls, db_session: AsyncSession):
        result = await db_session.execute(select(Club).options(selectinload(Club.players))) #сразу загрузка и игроков
        return result.scalars().all()


    @classmethod
    async def get_club_or_player_by_id(cls, delete_id: UUID, db_session: AsyncSession):
        club = await db_session.get(Club, delete_id).with_for_update(skip_locked=True)
        player = await db_session.get(Player, delete_id).with_for_update(skip_locked=True)
        return club, player


    @classmethod
    async def get_club_with_players(cls, club_id: UUID, db_session: AsyncSession):
        query = select(Club).where(Club.id == club_id).options(selectinload(Club.players)).with_for_update(skip_locked=True)
        result = await db_session.execute(query)
        return result.scalar_one_or_none()


    @classmethod
    async def get_player_by_id(cls, player_id: UUID, db_session: AsyncSession):
        query = select(Player).where(Player.id == player_id).with_for_update(skip_locked=True)
        result = await db_session.execute(query)
        return result.scalar_one_or_none()


    @classmethod
    async def update_info(cls, upd_object, db_session: AsyncSession):
        await db_session.flush()
        await db_session.refresh(upd_object)
        return upd_object


    @classmethod
    async def delete_club_or_player(cls, delete_obj, db_session: AsyncSession):
        await db_session.delete(delete_obj)
        return delete_obj