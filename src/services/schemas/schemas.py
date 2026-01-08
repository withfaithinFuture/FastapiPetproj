import datetime
from typing import List
from pydantic import Field, BaseModel
from uuid import UUID
from decimal import Decimal

letters = r'^[A-Za-zА-Яа-яЁё0-9\s\-]+$'

#клуб + футболисты (многие ко многим)
class ClubSchema(BaseModel):
    name: str = Field(min_length=3,  pattern=letters)
    home_town: str = Field(min_length=3,  pattern=letters)
    creation_date: datetime.date
    players: List["PlayerSchema"]

    class Config:
        from_attributes = True #принятие не только словарей но и других объектов с аттр


class ClubSchemaUpdate(BaseModel):
    id: UUID
    name: None | str = Field(min_length=3,  pattern=letters, default=None)
    home_town: None | str = Field(min_length=3,  pattern=letters, default=None)
    creation_date: None | datetime.date = Field(default=None)


class PlayerSchema(BaseModel):
    first_name: str = Field(min_length=3, pattern=letters)
    last_name: str = Field(min_length=3, pattern=letters)
    played_in_club: datetime.date

    class Config:
        from_attributes = True


class PlayerSchemaUpdate(BaseModel):
    id: UUID
    first_name: None | str = Field(min_length=3, pattern=letters)
    last_name: None | str = Field(min_length=3, pattern=letters)
    played_in_club: None | datetime.date


#биржа + владелец (1 к 1)
class ExchangeOwnerSchema(BaseModel):
    first_name: str = Field(min_length=2, pattern=letters)
    last_name: str = Field(min_length=2, pattern=letters)

    class Config:
        from_attributes = True


class ExchangeSchema(BaseModel):
    owner: ExchangeOwnerSchema
    exchange_name: str = Field(min_length=2, pattern=letters)
    work_in_Russia: bool
    volume: float

    class Config:
        from_attributes = True

class ExchangeUpdateSchema(BaseModel):
    id: UUID
    exchange_name: None | str = Field(min_length=2, pattern=letters)
    work_in_Russia: None | bool
    volume: None | float


class ExchangeOwnerUpdateSchema(BaseModel):
    id: UUID
    first_name: str = Field(min_length=2, pattern=letters)
    last_name: str = Field(min_length=2, pattern=letters)



#юзеры и акции (1 к многие)
class UserSchema(BaseModel):
    username: str = Field(min_length=3, pattern=letters)
    shares: List["SharesSchema"]

class UserSchemaUpdate(BaseModel):
    id: UUID
    username: str = Field(min_length=3, pattern=letters)

    class Config:
        from_attributes = True

class SharesSchema(BaseModel):
    ticker: None | str = Field(min_length=2, pattern=letters)
    quantity: float | int | None
    purchase_price: Decimal | int | None
    purchase_date: datetime.date | None

class SharesSchemaUpdate(BaseModel):
    id: UUID
    ticker: None | str = Field(min_length=2, pattern=letters)
    quantity: float | int | None
    purchase_price: Decimal | int | None
    purchase_date: datetime.date | None

    class Config:
        from_attributes = True