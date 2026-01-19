from uuid import UUID
from fastapi import APIRouter, Depends, status
from src.services.schemas.club_schemas import ClubSchemaUpdate, PlayerSchemaUpdate
from src.services.schemas.club_schemas import ClubSchema
from services.services.club_service import ClubService
from src.app.dependencies import get_club_service


router = APIRouter(tags=['Actions with football clubs'])

@router.post('/clubs', status_code=status.HTTP_201_CREATED)
async def add_club(club: ClubSchema, clsrv: ClubService = Depends(get_club_service)):
    return await clsrv.add_club_service(club)


@router.get('/clubs', status_code=status.HTTP_200_OK)
async def get_clubs(clsrv: ClubService = Depends(get_club_service)):
    return await clsrv.get_clubs_info_service()


@router.patch('/clubs/{club_id}', status_code=status.HTTP_200_OK)
async def update_clubs(club_id: UUID, club_update: ClubSchemaUpdate, clsrv: ClubService = Depends(get_club_service)):
    return await clsrv.update_clubs_info_service(club_id, club_update)


@router.patch('/clubs/{player_id}', status_code=status.HTTP_200_OK)
async def update_players(player_id: UUID, player_update: PlayerSchemaUpdate, clsrv: ClubService = Depends(get_club_service)):
    return await clsrv.update_players_info_service(player_id, player_update)


@router.delete('/clubs/{object_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(delete_id: UUID, clsrv: ClubService = Depends(get_club_service)):
    return await clsrv.delete_club_or_player(delete_id)