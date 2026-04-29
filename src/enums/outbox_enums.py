import enum

class OutboxStatus(str, enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    FAILED = "FAILED"
    SENT = "SENT"
