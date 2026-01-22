from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.football_players import Player
from src.models.clubs import Club



class ClubFootballersRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_club(self, club: Club, players: list[Player]) -> tuple[Club, list[Player]]:
        self.session.add(club)
        self.session.add_all(players)
        await self.session.flush()
        await self.session.refresh(club)
        return club, players


    async def get_clubs_info(self):
        result = await self.session.execute(select(Club).options(selectinload(Club.players)))
        return result.scalars().all()


    async def get_club_or_player_by_id(self, delete_id: UUID) -> tuple[Club | None, Player | None]:
        query_club = select(Club).where(Club.id == delete_id).with_for_update(skip_locked=True)
        query_player = select(Player).where(Player.id == delete_id).with_for_update(skip_locked=True)
        club = await self.session.execute(query_club)
        player = await self.session.execute(query_player)
        return club.scalar_one_or_none(), player.scalar_one_or_none()


    async def get_club_with_players(self, club_id: UUID) -> Club | None:
        query = select(Club).where(Club.id == club_id).options(selectinload(Club.players)).with_for_update(skip_locked=True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def get_player_by_id(self, player_id: UUID) -> Player | None:
        query = select(Player).where(Player.id == player_id).with_for_update(skip_locked=True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def update_info(self, upd_object):
        await self.session.flush()
        await self.session.refresh(upd_object)
        return upd_object


    async def delete_club_or_player(self, delete_obj):
        await self.session.delete(delete_obj)