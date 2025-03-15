from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from PyQt6.QtWidgets import QComboBox, QSpinBox
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
    
    def __post_init__(self):
        self.logger = Logger().get_logger('TableItemView')
        self.logger.debug(f"Создан объект TableItemView: {self.timestamp} - {self.name} - {self.event} - {self.alert_level}")

@dataclass
class GiftData:
    id: int
    name: str
    image: str
    
    def __post_init__(self):
        self.logger = Logger().get_logger('GiftData')
        self.logger.debug(f"Создан объект GiftData: ID {self.id}, имя: {self.name}, изображение: {self.image[:20]}...")  # Обрезаем изображение для краткости лога