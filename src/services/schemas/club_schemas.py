import datetime
from typing import List
from pydantic import Field, BaseModel

from src.services.schemas.player_schemas import PlayerSchema

letters = r'^[A-Za-zА-Яа-яЁё0-9\s\-]+$'


class ClubSchema(BaseModel):
    name: str = Field(min_length=3,  pattern=letters)
    home_town: str = Field(min_length=3,  pattern=letters)
    creation_date: datetime.date
    players: List["PlayerSchema"]

    class Config:
        from_attributes = True


class ClubSchemaUpdate(BaseModel):
    name: None | str = Field(min_length=3,  pattern=letters, default=None)
    home_town: None | str = Field(min_length=3,  pattern=letters, default=None)
    creation_date: None | datetime.date = Field(default=None)
