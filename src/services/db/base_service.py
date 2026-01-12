import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

metadata = sa.MetaData()


class BaseServiceModel:
    """Базовый класс для таблиц сервиса."""

    @classmethod
    def on_conflict_constraint(cls) -> tuple | None:
        return None

                        #привязка            #добавл каст методов
Base = declarative_base(metadata=metadata, cls=BaseServiceModel)