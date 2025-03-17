# events_table_model.py
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QPixmap, QImage
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
        self.viewmodel.item_added.connect(self.add_item)
    
    def rowCount(self, parent=QModelIndex()):
        count = len(self.viewmodel.item_list)
        self.logger.debug(f"Запрос количества строк: {count}")
        return count
    
    def columnCount(self, parent=QModelIndex()):
        count = len(self.headers)
        self.logger.debug(f"Запрос количества столбцов: {count}")
        return count
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.viewmodel.item_list)):
            self.logger.debug(f"Неверный индекс: {index}")
            return None
        item = self.viewmodel.item_list[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                value = item.timestamp.strftime("%H:%M:%S")
                self.logger.debug(f"Запрос данных для строки {index.row()}, столбца {index.column()}: {value}")
                return value
            elif index.column() == 1:
                value = item.name
                self.logger.debug(f"Запрос данных для строки {index.row()}, столбца {index.column()}: {value}")
                return value
            elif index.column() == 2:
                value = item.event
                self.logger.debug(f"Запрос данных для строки {index.row()}, столбца {index.column()}: {value}")
                return value
            elif index.column() == 3:
                value = item.alert_level.name
                self.logger.debug(f"Запрос данных для строки {index.row()}, столбца {index.column()}: {value}")
                return value
            elif index.column() == 4:
                value = item.gift_name
                self.logger.debug(f"Запрос данных для строки {index.row()}, столбца {index.column()}: {value}")
                return value
        elif role == Qt.ItemDataRole.DecorationRole:
            if index.column() == 4:
                if item.gift_image:
                    pixmap = self.base64_to_pixmap(item.gift_image)
                    self.logger.debug(f"Запрос изображения для строки {index.row()}, столбца {index.column()}")
                    return pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
        elif role == Qt.ItemDataRole.BackgroundRole:
            if item.alert_level == AlertLevel.IMPORTANT:
                self.logger.debug(f"Запрос фона для строки {index.row()} с уровнем важности: {item.alert_level}")
                return Qt.GlobalColor.yellow
        return None
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            value = self.headers[section]
            self.logger.debug(f"Запрос заголовка для секции {section}: {value}")
            return value
        return None
    
    def base64_to_pixmap(self, base64_string):
        image_data = QByteArray.fromBase64(base64_string.encode('utf-8'))
        image = QImage()
        image.loadFromData(image_data)
        pixmap = QPixmap.fromImage(image)
        self.logger.debug(f"Преобразование изображения из base64")
        return pixmap
    
    def add_item(self, item):
        """Добавляет новое событие в список и уведомляет модель о добавлении строки"""
        try:
            row = len(self.viewmodel.item_list)
            self.beginInsertRows(QModelIndex(), row, row)
            self.viewmodel.item_list.insert(0, item)  # Вставляем в начало списка
            self.endInsertRows()
            self.logger.debug(f"Добавлено новое событие: {item.timestamp} - {item.name} - {item.event}")
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении события в модель: {str(e)}", exc_info=True)
