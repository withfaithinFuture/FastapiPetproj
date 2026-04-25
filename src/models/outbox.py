from datetime import datetime, timezone
import sqlalchemy as sa
from uuid import UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base_service import Base
from src.enums.outbox_enums import OutboxStatus


class OutboxEvent(Base):
    __tablename__ = 'outbox_events'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    topic: Mapped[str] = mapped_column(sa.String(), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(sa.String(), default=OutboxStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=datetime.now)