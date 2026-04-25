import datetime as dt
from typing import List
from pydantic import Field, BaseModel, EmailStr, field_validator
from src.schemas.shares_schemas import SharesSchema
from src.core.age_validation import validate_age


letters = r'^[A-Za-zА-Яа-яЁё0-9\s\-]+$'
numbers = r'^\d{4}\-\d{2}\-\d{2}$'

class UserSchema(BaseModel):
    username: str = Field(min_length=3, pattern=letters)
    email: EmailStr
    age: dt.date = Field(examples=['2000-01-02'])
    shares_broker: str = Field(examples=['T-Bank', 'VTB', 'Sber', 'Alfa-Bank', 'Gazprombank'])
    user_shares: List["SharesSchema"]

    @field_validator('age')
    @classmethod
    def validate_age_data(cls, value: dt.date):
        value_string = str(value)
        year, month, day = map(int, value_string.split('-'))
        birth_date = dt.date(year, month, day)
        validate_age(birth_date)
        return value

    @field_validator('shares_broker')
    @classmethod
    def get_lowercase(cls, value: str) -> str:
        return value.lower()

    class Config:
        from_attributes = True


class UserSchemaUpdate(BaseModel):
    username: str = Field(min_length=3, pattern=letters)
    email: None | str = Field(min_length=4)
    age: dt.date = Field(examples=['2000-01-02'])

    @field_validator('age')
    @classmethod
    def validate_age_data(cls, value: dt.date):
        value_string = str(value)
        year, month, day = map(int, value_string.split('-'))
        birth_date = dt.date(year, month, day)
        validate_age(birth_date)
        return value


    class Config:
        from_attributes = True


class UserSharesFastResponseSchema(BaseModel):
    message: str = Field(default="Заявка на создание биржи принята")
    username: str = Field(min_length=2, pattern=letters)
    user_shares: List["SharesSchema"]