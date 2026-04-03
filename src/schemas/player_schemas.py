import datetime
from pydantic import Field, BaseModel


letters = r'^[A-Za-zА-Яа-яЁё0-9\s\-]+$'

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