from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.sql import func
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base_service import Base
from src.enums.outbox_enums import OutboxStatus


class OutboxEvent(Base):
    __tablename__ = 'outbox_events'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    topic: Mapped[str] = mapped_column(sa.String(), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(sa.String(), default=OutboxStatus.NEW, server_default=text(f"'{OutboxStatus.NEW}'"))
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, server_default=func.now())
    fix_attempts: Mapped[int] = mapped_column(sa.Integer, default=0, server_default='0')