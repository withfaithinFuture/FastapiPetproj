import datetime as dt
from pydantic import Field, BaseModel
from decimal import Decimal


letters = r'^[A-Za-zА-Яа-яЁё0-9\s\-]+$'
numbers = r'^\d{4}\-\d{2}\-\d{2}$'

class SharesSchema(BaseModel):
    ticker: None | str = Field(min_length=2, pattern=letters)
    quantity: float | int | None
    purchase_price: Decimal | int | None
    purchase_date: dt.date | None

    class Config:
        from_attributes = True


class SharesSchemaUpdate(BaseModel):
    ticker: None | str = Field(min_length=2, pattern=letters)
    quantity: float | int | None
    purchase_price: Decimal | int | None
    purchase_date: dt.date | None

    class Config:
        from_attributes = True