from pydantic import Field, BaseModel
from src.services.schemas.exchange_owners_schemas import ExchangeOwnerSchema


letters = r'^[A-Za-zА-Яа-яЁё0-9\s\-]+$'

class ExchangeCreateSchema(BaseModel):
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


class SecondServiceValidationSchema(BaseModel):
    trust_score: int = Field(lt=11)
    btc_price: float
    eth_price: float
    sol_price: float


class ExchangeResponseSchema(BaseModel):
    owner: ExchangeOwnerSchema
    exchange_name: str = Field(min_length=2, pattern=letters)
    work_in_Russia: bool
    volume: float
    trust_score: int = Field(lt=11)
    btc_price: float
    eth_price: float
    sol_price: float

    class Config:
        from_attributes = True