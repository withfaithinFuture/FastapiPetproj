from pydantic import Field, BaseModel


letters = r'^[A-Za-zА-Яа-яЁё0-9\s\-]+$'

class ExchangeOwnerSchema(BaseModel):
    first_name: str = Field(min_length=2, pattern=letters)
    last_name: str = Field(min_length=2, pattern=letters)

    class Config:
        from_attributes = True


class ExchangeOwnerUpdateSchema(BaseModel):
    first_name: None | str =  Field(min_length=2, pattern=letters)
    last_name: None | str = Field(min_length=2, pattern=letters)