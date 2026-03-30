import sqlalchemy as sa
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.enums.saga_enums import SagaStatus
from src.db.base_service import Base


class Exchange(Base):
    __tablename__ = 'exchanges'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey('exchange_owners.id', ondelete='CASCADE'), unique=True, default=uuid4)
    exchange_name: Mapped[str] = mapped_column(sa.String(), unique=True)
    work_in_russia: Mapped[bool] = mapped_column(sa.Boolean())
    volume: Mapped[float] = mapped_column(sa.Float())
    trust_score: Mapped[int | None] = mapped_column(sa.Integer())
    btc_price: Mapped[float | None] = mapped_column(sa.Float())
    eth_price: Mapped[float | None] = mapped_column(sa.Float())
    sol_price: Mapped[float | None] = mapped_column(sa.Float())
    status: Mapped[SagaStatus] = mapped_column(sa.Enum(SagaStatus, native_enum=False), default=SagaStatus.PENDING, nullable=False)

    owner = relationship('Owner', back_populates='exchange')
