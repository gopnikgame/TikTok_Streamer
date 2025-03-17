from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPixmap, QImage
from PyQt6.QtCore import QByteArray
from models.data_models import TableItemView, AlertLevel
from utils.logger import Logger
from datetime import datetime

class EventsTableModel(QAbstractTableModel):
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel
        self.headers = ["Время", "Пользователь", "Событие", "Уровень важности", "Подарок"]
        self.logger = Logger().get_logger('EventsTableModel')
        self.logger.info("Инициализация модели таблицы событий")
    
    def rowCount(self, parent=QModelIndex()):
        self.logger.debug(f"Запрос количества строк: {len(self.viewmodel.item_list)}")
        return len(self.viewmodel.item_list)
    
    def columnCount(self, parent=QModelIndex()):
        self.logger.debug(f"Запрос количества столбцов: {len(self.headers)}")
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.viewmodel.item_list)):
            self.logger.debug(f"Неверный индекс: {index}")
            return None
        item = self.viewmodel.item_list[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                self.logger.debug(f"Запрос данных для строки {index.row()}, столбца {index.column()}: {item.timestamp.strftime('%H:%M:%S')}")
                return item.timestamp.strftime("%H:%M:%S")
            elif index.column() == 1:
                self.logger.debug(f"Запрос данных для строки {index.row()}, столбца {index.column()}: {item.name}")
                return item.name
            elif index.column() == 2:
                self.logger.debug(f"Запрос данных для строки {index.row()}, столбца {index.column()}: {item.event}")
                return item.event
            elif index.column() == 3:
                self.logger.debug(f"Запрос данных для строки {index.row()}, столбца {index.column()}: {item.alert_level.name}")
                return item.alert_level.name
            elif index.column() == 4:
                self.logger.debug(f"Запрос данных для строки {index.row()}, столбца {index.column()}: {item.gift_name}")
                return item.gift_name
        elif role == Qt.ItemDataRole.DecorationRole:
            if index.column() == 4:
                if item.gift_image:
                    pixmap = self.base64_to_pixmap(item.gift_image)
                    return pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
        elif role == Qt.ItemDataRole.BackgroundRole:
            if item.alert_level == AlertLevel.IMPORTANT:
                self.logger.debug(f"Запрос фона для строки {index.row()} с уровнем важности: {item.alert_level}")
                return Qt.GlobalColor.yellow
        return None
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            self.logger.debug(f"Запрос заголовка для секции {section}: {self.headers[section]}")
            return self.headers[section]
        return None
    
    def base64_to_pixmap(self, base64_string):
        image_data = QByteArray.fromBase64(base64_string.encode('utf-8'))
        image = QImage()
        image.loadFromData(image_data)
        return QPixmap.fromImage(image)
