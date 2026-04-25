import enum

class OutboxStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"