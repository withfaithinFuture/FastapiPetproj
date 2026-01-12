import sqlalchemy as sa
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.db.base_service import Base

class Exchange(Base):
    __tablename__ = 'exchanges'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey('exchange_owners.id', ondelete='CASCADE'), unique=True, default=uuid4)
    exchange_name: Mapped[str] = mapped_column(sa.String())
    work_in_Russia: Mapped[bool] = mapped_column(sa.Boolean())
    volume: Mapped[float] = mapped_column(sa.Float())

    owner = relationship('Owner', back_populates='exchange')
