import sqlalchemy as sa
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.services.data_service import Base


class Owner(Base):
    __tablename__ = 'exchange_owners'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    first_name: Mapped[str] = mapped_column(sa.String())
    last_name: Mapped[str] = mapped_column(sa.String())

    exchange = relationship('Exchange', back_populates='owner', cascade='all, delete-orphan', uselist=False)