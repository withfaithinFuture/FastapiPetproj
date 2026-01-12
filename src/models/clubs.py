from typing import List
import sqlalchemy as sa
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.db.base_service import Base
from src.models.clubsandplayers import joined_table


class Club(Base):
    __tablename__ = 'clubs'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(sa.String())
    home_town: Mapped[str] = mapped_column(sa.String())
    creation_date: Mapped[sa.Date] = mapped_column(sa.Date())

    players: Mapped[List["Player"]] = relationship(secondary=joined_table, back_populates='clubs', lazy='selectin')