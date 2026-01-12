from typing import List
import sqlalchemy as sa
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.clubsandplayers import joined_table
from services.db.base_service import Base



class Player(Base):
    __tablename__ = 'players'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    first_name: Mapped[str] = mapped_column(sa.String())
    last_name: Mapped[str] = mapped_column(sa.String())
    played_in_club: Mapped[sa.Date] = mapped_column(sa.Date())

    clubs: Mapped[List["Club"]] = relationship(secondary=joined_table, back_populates='players')