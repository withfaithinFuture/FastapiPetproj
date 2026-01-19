import datetime
from typing import List
from pydantic import Field, BaseModel, validator, field_validator
from decimal import Decimal
from src.services.core.email_validation import validate_email_domain, validate_email_format


letters = r'^[A-Za-zА-Яа-яЁё0-9\s\-]+$'

class UserSchema(BaseModel):
    username: str = Field(min_length=3, pattern=letters)
    email: str = Field(min_length=4)
    user_shares: List["SharesSchema"]

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        validate_email_format(value)
        validate_email_domain(value)
        return value.lower()

    class Config:
        from_attributes = True

class UserSchemaUpdate(BaseModel):
    username: str = Field(min_length=3, pattern=letters)
    email: None | str = Field(min_length=4)

    if email:
        @field_validator('email')
        @classmethod
        def validate_email(cls, value):
            validate_email_format(value)
            validate_email_domain(value)
            return value.lower()

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