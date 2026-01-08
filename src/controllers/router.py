from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from src.services.repositories.shares_repo import UserSharesRepository
from src.services.exceptions import NothingExists, ValidationError
from src.services.repositories.exchanges_repo import ExchangesOwnersRepository
from src.services.dependencies import validate_exist_player, validate_exchange_exist, validate_owner_exist, validate_user_exist, validate_share_exist
from src.services.dependencies import validate_exist_club
from src.services.schemas.schemas import ClubSchemaUpdate, PlayerSchemaUpdate, ExchangeSchema, ExchangeUpdateSchema, \
    ExchangeOwnerUpdateSchema, UserSchema, UserSchemaUpdate, SharesSchemaUpdate
from src.services.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.repositories.clubs_repo import ClubFootballersRepository
from src.services.schemas.schemas import ClubSchema


router = APIRouter()

@router.get('/healthcheck')
async def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}


@router.post('/Клубы/Добавление клуба с игроками', tags=['Действия с футбольным клубами']) #через depends
async def add_club(club: ClubSchema, db_session: AsyncSession = Depends(get_session)):
    async with db_session.begin():
        club = await ClubFootballersRepository.add_club(club, db_session)
    return {'Club': club, 'HTTP status': 201}


@router.get('/Клубы/Получение', tags=['Действия с футбольным клубами'])
async def get_clubs(db_session: AsyncSession = Depends(get_session)):
    clubs = await ClubFootballersRepository.get_clubs_info(db_session)
    return {"Clubs": clubs, 'HTTP status': 200}


@router.patch('/Клубы/Обновление клубов', tags=['Действия с футбольным клубами'])
async def update_clubs(club_update: ClubSchemaUpdate, db_session: AsyncSession = Depends(get_session)):
    try:
        await validate_exist_club(club_update, db_session)
        async with db_session.begin():
            updated_club = await ClubFootballersRepository.update_clubs_info(club_update, db_session)
        return {'New club info': updated_club, 'HTTP status': 200}

    except ValidationError as e:
        raise HTTPException(status_code=404, detail={"error": str(e)})


@router.patch('/Клубы/Обновление игроков', tags=['Действия с футбольным клубами'])
async def update_players(player_update: PlayerSchemaUpdate, db_session: AsyncSession = Depends(get_session)):
    try:
        await validate_exist_player(player_update, db_session)
        async with db_session.begin():
            updated_player = await ClubFootballersRepository.update_players_info(player_update, db_session)
        return {'New player info': updated_player, 'HTTP status': 200}

    except ValidationError as e:
        raise HTTPException(status_code=404, detail={"error": str(e)})


@router.post('/Клубы/Удаление игрока или клуба', tags=['Действия с футбольным клубами'])
async def delete_by_id(delete_id: UUID, db_session: AsyncSession = Depends(get_session)):
    try:
        async with db_session.begin():
            deleted_object = await ClubFootballersRepository.delete_club_or_player(delete_id, db_session)
        return {'Deleted object': deleted_object, 'HTTP status': 200}

    except NothingExists as e:
        raise HTTPException(status_code=404, detail={"error": str(e)})


@router.post('/Биржа/Добавление биржи', tags=['Действия с биржами'])
async def add_exchange(exchange_data: ExchangeSchema, db_session: AsyncSession = Depends(get_session)):
    async with db_session.begin():
        new_exchange = await ExchangesOwnersRepository.add_exchange(exchange_data, db_session)
    return {'Exchange': new_exchange, 'HTTP status': 201}


@router.get('/Биржа/Получение бирж', tags=['Действия с биржами'])
async def get_exchanges(db_session: AsyncSession = Depends(get_session)):
    exchanges = await ExchangesOwnersRepository.get_exchanges_info(db_session)
    return {"Exchanges": exchanges, 'HTTP status': 200}


@router.patch('/Биржа/Обновление биржи', tags=['Действия с биржами'])
async def update_exchange(update_data: ExchangeUpdateSchema, db_session: AsyncSession = Depends(get_session)):

    try:
        await validate_exchange_exist(update_data, db_session)
        async with db_session.begin():
            updated_exchange = await ExchangesOwnersRepository.update_exchange_info(update_data, db_session)
        return {'New exchange info': updated_exchange, 'HTTP status': 200}

    except ValidationError as e:
        raise HTTPException(status_code=404, detail={'error': str(e)})


@router.patch('/Биржа/Обновление создателя биржи', tags=['Действия с биржами'])
async def update_owner(update_data: ExchangeOwnerUpdateSchema, db_session: AsyncSession = Depends(get_session)):

    try:
        await validate_owner_exist(update_data, db_session)
        async with db_session.begin():
            updated_owner = await ExchangesOwnersRepository.update_owner_info(update_data, db_session)
        return {'New owner info': updated_owner, 'HTTP status': 200}

    except ValidationError as e:
        raise HTTPException(status_code=404, detail={'error': str(e)})


@router.post('/Биржа/Удаление биржи с создателем', tags=['Действия с биржами'])
async def delete_exchange(delete_id: UUID, db_session: AsyncSession = Depends(get_session)):

    try:
        async with db_session.begin():
            deleted_object = await ExchangesOwnersRepository.delete_exchange_info(delete_id, db_session)
        return {'Deleted object': deleted_object, 'HTTP status': 200}

    except NothingExists as e:
        raise HTTPException(status_code=404, detail={'error': str(e)})


@router.post('/Акции/Добавление акций с их владельцем', tags=['Действия с акциями'])
async def add_shares(user_data: UserSchema, db_session: AsyncSession = Depends(get_session)):
    async with db_session.begin():
        new_data = await UserSharesRepository.add_shares(user_data, db_session)
    return {'Shares': new_data, 'HTTP status': 201}


@router.get('/Акции/Получение акций с их владельцем', tags=['Действия с акциями'])
async def get_shares(db_session: AsyncSession = Depends(get_session)):
    all_data = await UserSharesRepository.get_shares_info(db_session)
    return {'All data': all_data, 'HTTP status': 200}


@router.patch('/Акции/Обновление информации владельца акций', tags=['Действия с акциями'])
async def update_user_shares(update_data: UserSchemaUpdate, db_session: AsyncSession = Depends(get_session)):
    try:
        await validate_user_exist(update_data, db_session)
        async with db_session.begin():
            updated_user = await UserSharesRepository.update_user_shares_info(update_data, db_session)
        return  {'New user info': updated_user, 'HTTP status': 200}

    except ValidationError as e:
        raise HTTPException(status_code=404, detail={'error': str(e)})


@router.patch('/Акции/Обновление информации акций', tags=['Действия с акциями'])
async def update_user_shares(update_data: SharesSchemaUpdate, db_session: AsyncSession = Depends(get_session)):
    try:
        await validate_share_exist(update_data, db_session)
        async with db_session.begin():
            updated_share = await UserSharesRepository.update_shares_info(update_data, db_session)
        return  {'New user info': updated_share, 'HTTP status': 200}

    except ValidationError as e:
        raise HTTPException(status_code=404, detail={'error': str(e)})


@router.post('/Акции/Удаление юзера или акций', tags=['Действия с акциями'])
async def delete_exchange(delete_id: UUID, db_session: AsyncSession = Depends(get_session)):

    try:
        async with db_session.begin():
            deleted_object = await UserSharesRepository.delete_owner_or_share(delete_id, db_session)
        return  {'Deleted object': deleted_object, 'HTTP status': 200}

    except NothingExists as e:
        raise HTTPException(status_code=404, detail={'error': str(e)})