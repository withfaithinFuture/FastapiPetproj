from uuid import UUID
from fastapi import APIRouter, Depends
from src.services.schemas.club_schemas import ClubSchemaUpdate, PlayerSchemaUpdate
from src.services.db.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.schemas.club_schemas import ClubSchema
from src.services.club_service import ClubService


router = APIRouter()

def get_club_service(session: AsyncSession = Depends(get_session)) -> ClubService:
    return ClubService(session)


@router.post('/Clubs/Add', tags=['Actions with football clubs'])
async def add_club(club: ClubSchema, clsrv: ClubService = Depends(get_club_service)):
    return await clsrv.add_club_service(club)


@router.get('/Clubs/Get', tags=['Actions with football clubs'])
async def get_clubs(clsrv: ClubService = Depends(get_club_service)):
    return await clsrv.get_clubs_info_service()


@router.patch('/Clubs/UpdateClubs', tags=['Actions with football clubs'])
async def update_clubs(club_id: UUID, club_update: ClubSchemaUpdate, clsrv: ClubService = Depends(get_club_service)):
    return await clsrv.update_clubs_info_service(club_id, club_update)


@router.patch('/Clubs/UpdatePlayers', tags=['Actions with football clubs'])
async def update_players(player_id: UUID, player_update: PlayerSchemaUpdate, clsrv: ClubService = Depends(get_club_service)):
    return await clsrv.update_players_info_service(player_id, player_update)


@router.post('/Clubs/Delete', tags=['Actions with football clubs'])
async def delete_by_id(delete_id: UUID, clsrv: ClubService = Depends(get_club_service)):
    return await clsrv.delete_club_or_player(delete_id)