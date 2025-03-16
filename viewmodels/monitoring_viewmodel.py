import os
import threading
import asyncio
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from models.data_models import TableItemView, AlertLevel
from utils.settings import Settings
from utils.logger import Logger
from utils.error_handler import ErrorHandler
from monitoring_worker import MonitoringWorker
from datetime import datetime
from services.gift_service import GiftService

class MonitoringViewModel(QObject):
    status_changed = pyqtSignal(str)
    item_added = pyqtSignal(TableItemView)

    def __init__(self, speech_service, sound_service, gift_service):
        super().__init__()
        self.logger = Logger().get_logger('MonitoringViewModel')
        self.logger.info("Инициализация ViewModel мониторинга")
        self.speech_service = speech_service
        self.sound_service = sound_service
        self.gift_service = gift_service
        self.settings = Settings()
        self.error_handler = ErrorHandler()
        # Свойства для привязки к UI
        self._is_monitoring = False
        self._is_processing = False
        self._stream = self.settings.user_id
        self._notify_gift = self.settings.notify_gift
        self._speech_gift = self.settings.speech_gift
        self._speech_like = self.settings.speech_like
        self._speech_member = self.settings.speech_member
        # Список событий для отображения
        self.item_list = []
        # Клиент TikTok
        self.worker = None
        self.thread = None
        self.logger.debug("ViewModel мониторинга инициализирован")

    # Свойства с уведомлением об изменении
    @property
    def is_monitoring(self):
        return self._is_monitoring

    @is_monitoring.setter
    def is_monitoring(self, value):
        if self._is_monitoring != value:
            self._is_monitoring = value
            self.logger.debug(f"Состояние мониторинга изменено: {value}")
            self.status_changed.emit(f"Состояние мониторинга: {value}")

    @property
    def is_processing(self):
        return self._is_processing

    @is_processing.setter
    def is_processing(self, value):
        if self._is_processing != value:
            self._is_processing = value
            self.logger.debug(f"Состояние обработки изменено: {value}")

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, value):
        if self._stream != value:
            self._stream = value
            self.settings.user_id = value
            self.settings.save()
            self.logger.debug(f"ID стрима изменен: {value}")

    @property
    def notify_gift(self):
        return self._notify_gift

    @notify_gift.setter
    def notify_gift(self, value):
        if self._notify_gift != value:
            self._notify_gift = value
            self.settings.notify_gift = value
            self.settings.save()
            self.logger.debug(f"Настройка звуковых оповещений изменена: {value}")

    @property
    def speech_gift(self):
        return self._speech_gift

    @speech_gift.setter
    def speech_gift(self, value):
        if self._speech_gift != value:
            self._speech_gift = value
            self.settings.speech_gift = value
            self.settings.save()
            self.logger.debug(f"Настройка озвучивания подарков изменена: {value}")

    @property
    def speech_like(self):
        return self._speech_like

    @speech_like.setter
    def speech_like(self, value):
        if self._speech_like != value:
            self._speech_like = value
            self.settings.speech_like = value
            self.settings.save()
            self.logger.debug(f"Настройка озвучивания лайков изменена: {value}")

    @property
    def speech_member(self):
        return self._speech_member

    @speech_member.setter
    def speech_member(self, value):
        if self._speech_member != value:
            self._speech_member = value
            self.settings.speech_member = value
            self.settings.save()
            self.logger.debug(f"Настройка озвучивания подключений изменена: {value}")

    def add_item(self, item):
        """Добавляет новое событие в список"""
        try:
            self.item_list.insert(0, item)
            if len(self.item_list) > 1000:
                self.item_list.pop()
            self.logger.debug(f"Добавлено событие: {item.timestamp} - {item.name} - {item.event}")
            self.item_added.emit(item)
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении события в список: {str(e)}")

    def start_monitoring(self):
        """Запускает мониторинг стрима TikTok"""
        if self.is_monitoring:
            self.logger.info("Остановка мониторинга текущего стрима")
            self.stop_monitoring()
            return
        if not self.stream:
            self.logger.warning("Попытка запуска мониторинга без указанного ID стрима")
            self.error_handler.show_validation_error(None, "Пожалуйста, укажите ID стрима TikTok")
            return
        self.logger.info(f"Запуск мониторинга стрима: {self.stream}")
        self.is_processing = True
        self.item_list.clear()
        self.status_changed.emit("Подключение...")
        self.worker = MonitoringWorker(self.stream, self.settings, self.speech_service, self.sound_service, self.gift_service)
        self.worker.status_changed.connect(self.on_status_changed)
        self.worker.item_added.connect(self.on_item_added)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.on_thread_finished)
        self.thread.start()

    def stop_monitoring(self):
        """Останавливает мониторинг стрима"""
        if self.worker and self.thread.isRunning():
            try:
                self.logger.info("Остановка мониторинга стрима")
                if self.worker.client_task:
                    self.worker.client_task.cancel()
                    self.logger.debug("Задача клиента отменена")
                asyncio.run_coroutine_threadsafe(self.worker.client.disconnect(), self.worker.loop)
            except Exception as e:
                self.logger.error(f"Ошибка при остановке клиента: {str(e)}")
                self.error_handler.handle_tiktok_error(None, e)
        self.is_monitoring = False
        self.is_processing = False
        self.logger.info("Мониторинг остановлен")

    def on_status_changed(self, status):
        self.status_changed.emit(status)

    def on_item_added(self, item):
        self.add_item(item)

    def on_thread_finished(self):
        self.logger.debug("Поток завершен")
        self.is_monitoring = False
        self.is_processing = False
        self.status_changed.emit("Мониторинг остановлен")