import datetime
from typing import List
from pydantic import Field, BaseModel
from uuid import UUID
from decimal import Decimal

letters = r'^[A-Za-zА-Яа-яЁё0-9\s\-]+$'

class UserSchema(BaseModel):
    username: str = Field(min_length=3, pattern=letters)
    user_shares: List["SharesSchema"]

    class Config:
        from_attributes = True

class UserSchemaUpdate(BaseModel):
    username: str = Field(min_length=3, pattern=letters)

    class Config:
        from_attributes = True

class SharesSchema(BaseModel):
    ticker: None | str = Field(min_length=2, pattern=letters)
    quantity: float | int | None
    purchase_price: Decimal | int | None
    purchase_date: datetime.date | None

    class Config:
        from_attributes = True

class SharesSchemaUpdate(BaseModel):
    ticker: None | str = Field(min_length=2, pattern=letters)
    quantity: float | int | None
    purchase_price: Decimal | int | None
    purchase_date: datetime.date | None

    class Config:
        from_attributes = True