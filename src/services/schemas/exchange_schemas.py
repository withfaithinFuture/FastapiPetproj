from pydantic import Field, BaseModel
from src.services.schemas.exchange_owners_schemas import ExchangeOwnerSchema


letters = r'^[A-Za-zА-Яа-яЁё0-9\s\-]+$'

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