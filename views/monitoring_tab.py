# monitoring_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QCheckBox, QTableView
from PyQt6.QtCore import Qt, QModelIndex
from models.data_models import AlertLevel, TableItemView, GiftData
from utils.error_handler import ErrorHandler
from utils.logger import Logger
from PyQt6 import sip
from datetime import datetime
from .events_table_model import EventsTableModel  # Импортируем EventsTableModel из отдельного файла

class MonitoringTab(QWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.error_handler = ErrorHandler()
        self.logger = Logger().get_logger('MonitoringTab')
        self.logger.info("Инициализация вкладки мониторинга")
        self.init_ui()
        self.bind_events()
        self.update_monitoring_state()
        self.logger.debug("Вкладка мониторинга инициализирована")
    
    def init_ui(self):
        """Инициализирует пользовательский интерфейс вкладки мониторинга"""
        try:
            layout = QVBoxLayout()
            # Строка с полем для ID стрима и кнопкой запуска
            stream_layout = QHBoxLayout()
            stream_label = QLabel("ID стрима:")
            self.stream_input = QLineEdit()
            self.stream_input.setText(self.viewmodel.stream)
            self.toggle_btn = QPushButton("Начать мониторинг")
            stream_layout.addWidget(stream_label)
            stream_layout.addWidget(self.stream_input, 1)
            stream_layout.addWidget(self.toggle_btn)
            layout.addLayout(stream_layout)
            self.logger.debug("Создана строка для ID стрима и кнопки запуска")
            # Чекбоксы для настроек
            checks_layout = QHBoxLayout()
            self.notify_chk = QCheckBox("Звуковое оповещение")
            self.notify_chk.setChecked(self.viewmodel.notify_gift)
            self.speech_gift_chk = QCheckBox("Озвучивать подарки")
            self.speech_gift_chk.setChecked(self.viewmodel.speech_gift)
            self.speech_like_chk = QCheckBox("Озвучивать лайки")
            self.speech_like_chk.setChecked(self.viewmodel.speech_like)
            self.speech_member_chk = QCheckBox("Озвучивать подключения")
            self.speech_member_chk.setChecked(self.viewmodel.speech_member)
            checks_layout.addWidget(self.notify_chk)
            checks_layout.addWidget(self.speech_gift_chk)
            checks_layout.addWidget(self.speech_like_chk)
            checks_layout.addWidget(self.speech_member_chk)
            layout.addLayout(checks_layout)
            self.logger.debug("Созданы чекбоксы для настроек")
            # Таблица событий
            self.table_model = EventsTableModel(self.viewmodel)
            self.table_view = QTableView()
            self.table_view.setModel(self.table_model)
            self.table_view.horizontalHeader().setStretchLastSection(True)
            layout.addWidget(self.table_view, 1)
            self.logger.debug("Создана таблица событий")
            # Статус
            self.status_label = QLabel("Статус: Готов к мониторингу")
            layout.addWidget(self.status_label)
            self.setLayout(layout)
        except Exception as e:
            self.logger.error(f"Ошибка при создании вкладки мониторинга: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка создания интерфейса", 
                                              "Не удалось создать вкладку мониторинга", str(e))
    
    def bind_events(self):
        """Привязывает обработчики событий к изменениям ViewModel"""
        try:
            self.toggle_btn.clicked.connect(self.toggle_monitoring)
            self.notify_chk.clicked.connect(self.toggle_notify_gift)
            self.speech_gift_chk.clicked.connect(self.toggle_speech_gift)
            self.speech_like_chk.clicked.connect(self.toggle_speech_like)
            self.speech_member_chk.clicked.connect(self.toggle_speech_member)
            self.viewmodel.status_changed.connect(self.update_status_label)
            self.viewmodel.item_added.connect(self.table_model.add_item)
            self.logger.debug("Обработчики событий привязаны")
        except Exception as e:
            self.logger.error(f"Ошибка при привязке обработчиков событий: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка инициализации", 
                                             "Не удалось привязать обработчики событий", str(e))
    
    def update_monitoring_state(self):
        """Обновляет состояние интерфейса в зависимости от статуса мониторинга"""
        try:
            if self.viewmodel.is_processing:
                self.toggle_btn.setEnabled(False)
                self.status_label.setText("Статус: Подключение...")
                self.stream_input.setEnabled(False)
                self.logger.debug("Обновлено состояние: Подключение...")
            elif self.viewmodel.is_monitoring:
                self.toggle_btn.setText("Остановить мониторинг")
                self.toggle_btn.setEnabled(True)
                self.status_label.setText(f"Статус: Мониторинг стрима {self.viewmodel.stream}")
                self.stream_input.setEnabled(False)
                self.logger.debug(f"Обновлено состояние: Мониторинг стрима {self.viewmodel.stream}")
            else:
                self.toggle_btn.setText("Начать мониторинг")
                self.toggle_btn.setEnabled(True)
                self.status_label.setText("Статус: Готов к мониторингу")
                self.stream_input.setEnabled(True)
                self.logger.debug("Обновлено состояние: Готов к мониторингу")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении состояния мониторинга: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка обновления интерфейса", 
                                             "Не удалось обновить состояние интерфейса", str(e))
    
    def update_status_label(self, status):
        """Обновляет текст статуса"""
        try:
            self.status_label.setText(f"Статус: {status}")
            self.logger.debug(f"Статус обновлен: {status}")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении статуса: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка обновления статуса", 
                                                 "Не удалось обновить статус", str(e))
    
    def toggle_monitoring(self):
        """Включает или выключает мониторинг"""
        try:
            if self.viewmodel.is_monitoring:
                self.logger.info("Остановка мониторинга")
                self.viewmodel.stop_monitoring()
                return
            # Получаем ID стрима из поля ввода
            stream = self.stream_input.text().strip()
            if not stream:
                self.logger.warning("Попытка начать мониторинг без указания ID стрима")
                self.error_handler.show_validation_error(self, "Пожалуйста, укажите ID стрима")
                return
            # Обновляем ID стрима в модели и запускаем мониторинг
            self.logger.info(f"Начало мониторинга стрима: {stream}")
            self.viewmodel.stream = stream
            self.viewmodel.start_monitoring()
        except Exception as e:
            self.logger.error(f"Ошибка при переключении мониторинга: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка мониторинга", 
                                                 "Не удалось изменить состояние мониторинга", str(e))
    
    def toggle_notify_gift(self):
        """Включает или выключает звуковые оповещения о подарках"""
        try:
            self.viewmodel.notify_gift = self.notify_chk.isChecked()
            self.logger.debug(f"Настройка звуковых оповещений изменена: {self.viewmodel.notify_gift}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении настройки звуковых оповещений: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                                 "Не удалось изменить настройку звуковых оповещений", str(e))
    
    def toggle_speech_gift(self):
        """Включает или выключает озвучивание подарков"""
        try:
            self.viewmodel.speech_gift = self.speech_gift_chk.isChecked()
            self.logger.debug(f"Настройка озвучивания подарков изменена: {self.viewmodel.speech_gift}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении настройки озвучивания подарков: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                                 "Не удалось изменить настройку озвучивания подарков", str(e))
    
    def toggle_speech_like(self):
        """Включает или выключает озвучивание лайков"""
        try:
            self.viewmodel.speech_like = self.speech_like_chk.isChecked()
            self.logger.debug(f"Настройка озвучивания лайков изменена: {self.viewmodel.speech_like}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении настройки озвучивания лайков: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                                 "Не удалось изменить настройку озвучивания лайков", str(e))
    
    def toggle_speech_member(self):
        """Включает или выключает озвучивание подключений"""
        try:
            self.viewmodel.speech_member = self.speech_member_chk.isChecked()
            self.logger.debug(f"Настройка озвучивания подключений изменена: {self.viewmodel.speech_member}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении настройки озвучивания подключений: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                                 "Не удалось изменить настройку озвучивания подключений", str(e))
