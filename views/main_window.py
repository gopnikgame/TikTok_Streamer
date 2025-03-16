# views/main_window.py
import os
import threading
from PyQt6.QtWidgets import QMainWindow, QTabWidget
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPixmap, QImage
from PyQt6 import sip
from models.data_models import AlertLevel, TableItemView, GiftData
from utils.error_handler import ErrorHandler
from utils.logger import Logger
from services.gift_service import GiftService
from services.speech_service import SpeechService
from services.sound_service import SoundService
from utils.settings import Settings
from viewmodels.monitoring_viewmodel import MonitoringViewModel
from PyQt6.QtCore import QByteArray
from datetime import datetime
from .monitoring_tab import MonitoringTab
from .settings_tab import SettingsTab
from .sounds_tab import SoundsTab

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

class MainWindow(QMainWindow):
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel
        self.error_handler = ErrorHandler()
        self.logger = Logger().get_logger('MainWindow')
        self.logger.info("Инициализация главного окна")
        # Инициализируем UI
        self.init_ui()
        # Привязываем обработчики событий
        self.bind_events()
        # Обновляем состояние UI
        self.update_monitoring_state()
        self.logger.debug("Главное окно инициализировано")
    
    def init_ui(self):
        """Инициализирует пользовательский интерфейс"""
        try:
            self.setWindowTitle("TTStreamerPy")
            self.resize(800, 600)
            # Создаем вкладки
            tabs = QTabWidget()
            tabs.addTab(MonitoringTab(self.viewmodel, self), "Мониторинг")
            tabs.addTab(SettingsTab(self.viewmodel, self), "Настройки")
            tabs.addTab(SoundsTab(self.viewmodel, self), "Звуки")
            # Устанавливаем основной виджет
            self.setCentralWidget(tabs)
            self.logger.debug("Интерфейс инициализирован")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации интерфейса: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка инициализации интерфейса", 
                                              "Не удалось инициализировать пользовательский интерфейс", str(e))
    
    def bind_events(self):
        """Привязывает обработчики событий к изменениям ViewModel"""
        try:
            self.viewmodel.item_added.connect(self.update_events_table)
            self.viewmodel.status_changed.connect(self.update_status)
            self.logger.debug("Обработчики событий привязаны")
        except Exception as e:
            self.logger.error(f"Ошибка при привязке обработчиков событий: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка инициализации", 
                                             "Не удалось привязать обработчики событий", str(e))
    
    def update_monitoring_state(self):
        """Обновляет состояние интерфейса в зависимости от статуса мониторинга"""
        try:
            if self.viewmodel.is_processing:
                self.logger.debug("Обновлено состояние: Подключение...")
            elif self.viewmodel.is_monitoring:
                self.logger.debug(f"Обновлено состояние: Мониторинг стрима {self.viewmodel.stream}")
            else:
                self.logger.debug("Обновлено состояние: Готов к мониторингу")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении состояния мониторинга: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка обновления интерфейса", 
                                             "Не удалось обновить состояние интерфейса", str(e))
    
    def update_events_table(self):
        """Обновляет таблицу событий"""
        try:
            if hasattr(self, 'table_model') and self.table_model:
                # Проверяем, что объект всё ещё существует и не был удалён
                if sip.isdeleted(self.table_model):
                    self.logger.warning("Объект table_model был удалён, создаём новый")
                    return
                self.table_model.layoutChanged.emit()
                self.logger.debug("Таблица событий обновлена")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении таблицы событий: {str(e)}")
            try:
                self.error_handler.handle_update_error(None, e)
            except Exception as inner_e:
                self.logger.error(f"Ошибка при обработке ошибки: {str(inner_e)}")
    
    def closeEvent(self, event):
        """Обработчик события закрытия окна"""
        self.logger.info("Закрытие главного окна")
        try:
            # Остановка мониторинга перед закрытием
            if self.viewmodel.is_monitoring:
                self.logger.debug("Остановка мониторинга перед закрытием окна")
                self.viewmodel.stop_monitoring()
            # Освобождение ресурсов
            if hasattr(self, 'table_model') and self.table_model:
                self.logger.debug("Освобождение ресурсов таблицы")
                self.table_view.setModel(None)  # Отсоединяем модель от представления
            # Вызываем стандартный обработчик закрытия окна
            super().closeEvent(event)
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии окна: {str(e)}")
            # Принудительно завершаем приложение в случае ошибки
            event.accept()
    
    def update_status(self, status):
        """Обновляет статус в интерфейсе"""
        try:
            self.status_label.setText(f"Статус: {status}")
            self.logger.info(f"Статус обновлен: {status}")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении статуса: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка обновления статуса", 
                                                 "Не удалось обновить статус", str(e))