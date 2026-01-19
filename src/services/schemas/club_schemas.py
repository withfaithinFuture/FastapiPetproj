import datetime
from typing import List
from pydantic import Field, BaseModel


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


class PlayerSchema(BaseModel):
    first_name: str = Field(min_length=3, pattern=letters)
    last_name: str = Field(min_length=3, pattern=letters)
    played_in_club: datetime.date

    class Config:
        from_attributes = True


class PlayerSchemaUpdate(BaseModel):
    first_name: None | str = Field(min_length=3, pattern=letters)
    last_name: None | str = Field(min_length=3, pattern=letters)
    played_in_club: None | datetime.date