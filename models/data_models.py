from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum

class AlertLevel(IntEnum):
    NORMAL = 0
    IMPORTANT = 1

@dataclass
class TableItemView:
    timestamp: datetime
    name: str
    event: str
    alert_level: AlertLevel = AlertLevel.NORMAL

@dataclass
class GiftData:
    id: int
    name: str
    image: str