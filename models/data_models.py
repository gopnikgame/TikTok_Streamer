from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from utils.logger import Logger

class AlertLevel(IntEnum):
    NORMAL = 0
    IMPORTANT = 1

@dataclass
class TableItemView:
    timestamp: datetime
    name: str
    event: str
    alert_level: AlertLevel = AlertLevel.NORMAL
    gift_name: str = ""  # Название подарка
    gift_image: str = ""  # base64-encoded изображение подарка
    
    def __post_init__(self):
        self.logger = Logger().get_logger('TableItemView')
        self.logger.debug(f"Создан объект TableItemView: {self.timestamp} - {self.name} - {self.event} - {self.alert_level} - {self.gift_name} - {self.gift_image[:20]}...")

@dataclass
class GiftData:
    id: int
    name: str
    image: str
    
    def __post_init__(self):
        self.logger = Logger().get_logger('GiftData')
        self.logger.debug(f"Создан объект GiftData: ID {self.id}, имя: {self.name}, изображение: {self.image[:20]}...")  # Обрезаем изображение для краткости лога