import datetime
from typing import List
from pydantic import Field, BaseModel
from uuid import UUID
from decimal import Decimal

letters = r'^[A-Za-zА-Яа-яЁё0-9\s\-]+$'

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
    exchange_name: None | str = Field(min_length=2, pattern=letters)
    work_in_Russia: None | bool
    volume: None | float


class ExchangeOwnerUpdateSchema(BaseModel):
    first_name: None | str =  Field(min_length=2, pattern=letters)
    last_name: None | str = Field(min_length=2, pattern=letters)