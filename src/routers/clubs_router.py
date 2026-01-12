from uuid import UUID
from fastapi import APIRouter, Depends
from src.services.schemas.club_schemas import ClubSchemaUpdate, PlayerSchemaUpdate
from src.services.db.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.schemas.club_schemas import ClubSchema
from src.services.club_service import ClubService as ClSrv


router = APIRouter()

@router.post('/Клубы/Добавление клуба с игроками', tags=['Действия с футбольным клубами']) #через depends
async def add_club(club: ClubSchema, db_session: AsyncSession = Depends(get_session)):
    new_club = await ClSrv.add_club_service(club, db_session)
    return {'Club': new_club, 'HTTP status': 201}


@router.get('/Клубы/Получение', tags=['Действия с футбольным клубами'])
async def get_clubs(db_session: AsyncSession = Depends(get_session)):
    clubs = await ClSrv.get_clubs_info_service(db_session)
    return {"Clubs": clubs, 'HTTP status': 200}


@router.patch('/Клубы/Обновление клубов', tags=['Действия с футбольным клубами'])
async def update_clubs(club_id: UUID, club_update: ClubSchemaUpdate, db_session: AsyncSession = Depends(get_session)):
    updated_club = await ClSrv.update_clubs_info_service(club_id, club_update, db_session)
    return {'New club info': updated_club, 'HTTP status': 200}


@router.patch('/Клубы/Обновление игроков', tags=['Действия с футбольным клубами'])
async def update_players(player_id: UUID, player_update: PlayerSchemaUpdate, db_session: AsyncSession = Depends(get_session)):
    updated_player = await ClSrv.update_players_info_service(player_id, player_update, db_session)
    return {'New player info': updated_player, 'HTTP status': 200}


@router.post('/Клубы/Удаление игрока или клуба', tags=['Действия с футбольным клубами'])
async def delete_by_id(delete_id: UUID, db_session: AsyncSession = Depends(get_session)):
    deleted_object = await ClSrv.delete_club_or_player(delete_id, db_session)
    return {'Deleted object': deleted_object, 'HTTP status': 200}