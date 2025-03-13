import asyncio
import threading
from datetime import datetime
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import GiftEvent, LikeEvent, JoinEvent, ConnectEvent, DisconnectEvent

from models.data_models import TableItemView, AlertLevel
from utils.settings import Settings
from utils.logger import Logger

class Observable:
    def __init__(self):
        self._callbacks = {}
        
    def add_callback(self, property_name, callback):
        if property_name not in self._callbacks:
            self._callbacks[property_name] = []
        self._callbacks[property_name].append(callback)
        
    def notify_property_changed(self, property_name):
        if property_name in self._callbacks:
            for callback in self._callbacks[property_name]:
                callback()

class MonitoringViewModel(Observable):
    def __init__(self, speech_service, sound_service, gift_service):
        super().__init__()
        self.logger = Logger().get_logger('MonitoringViewModel')
        self.logger.info("Инициализация ViewModel мониторинга")
        
        self.speech_service = speech_service
        self.sound_service = sound_service
        self.gift_service = gift_service
        self.settings = Settings()
        
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
        self.client = None
        self.client_task = None
        self.loop = None
        
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
            self.notify_property_changed('is_monitoring')
    
    @property
    def is_processing(self):
        return self._is_processing
        
    @is_processing.setter
    def is_processing(self, value):
        if self._is_processing != value:
            self._is_processing = value
            self.logger.debug(f"Состояние обработки изменено: {value}")
            self.notify_property_changed('is_processing')
    
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
            self.notify_property_changed('stream')
    
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
            self.notify_property_changed('notify_gift')
    
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
            self.notify_property_changed('speech_gift')
    
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
            self.notify_property_changed('speech_like')
    
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
            self.notify_property_changed('speech_member')
    
    def add_item(self, item):
        """Добавляет новое событие в список"""
        self.item_list.insert(0, item)
        if len(self.item_list) > 1000:
            self.item_list.pop()
        self.logger.debug(f"Добавлено событие: {item.timestamp} - {item.name} - {item.event}")
        self.notify_property_changed('item_list')