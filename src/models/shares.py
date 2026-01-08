import sqlalchemy as sa
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.services.data_service import Base


class Share(Base):
    __tablename__ = 'shares'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete = 'CASCADE'), default=uuid4)
    ticker: Mapped[str] = mapped_column(sa.String())
    quantity: Mapped[float] = mapped_column(sa.Float())
    purchase_price: Mapped[sa.Numeric] = mapped_column(sa.Numeric())
    purchase_date: Mapped[sa.Date] = mapped_column(sa.Date())

    owner_share = relationship('User', back_populates='user_shares')