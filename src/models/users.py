import sqlalchemy as sa
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.services.db.base_service import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(sa.String())
    email: Mapped[str] = mapped_column(sa.String())

    user_shares = relationship('Share', back_populates='owner_share', cascade='all, delete-orphan', lazy='selectin')
