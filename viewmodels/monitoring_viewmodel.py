import asyncio
import threading
from datetime import datetime
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import GiftEvent, LikeEvent, JoinEvent, ConnectEvent, DisconnectEvent

from models.data_models import TableItemView, AlertLevel
from utils.settings import Settings

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
    
    # Свойства с уведомлением об изменении
    @property
    def is_monitoring(self):
        return self._is_monitoring
        
    @is_monitoring.setter
    def is_monitoring(self, value):
        if self._is_monitoring != value:
            self._is_monitoring = value
            self.notify_property_changed('is_monitoring')
    
    @property
    def is_processing(self):
        return self._is_processing
        
    @is_processing.setter
    def is_processing(self, value):
        if self._is_processing != value:
            self._is_processing = value
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
            self.notify_property_changed('speech_member')
    
    def add_item(self, item):
        """Добавляет новое событие в список"""
        self.item_list.insert(0, item)
        if len(self.item_list) > 1000:
            self.item_list.pop()
        self.notify_property_changed('item_list')

    def start_monitoring(self):
        """Запускает мониторинг стрима TikTok"""
        if self.is_monitoring:
            self.stop_monitoring()
            return
        
        if not self.stream:
            return
        
        self.is_processing = True
        self.item_list.clear()
        self.notify_property_changed('item_list')
        
        # Запускаем клиент TikTok в отдельном потоке
        threading.Thread(target=self._run_tiktok_client, daemon=True).start()
    
    def _run_tiktok_client(self):
        """Запускает клиент TikTok Live в отдельном потоке"""
        try:
            # Создаем новый event loop для асинхронного кода
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Создаем клиент и регистрируем обработчики событий
            self.client = TikTokLiveClient(self.stream)
            
            # Обработчик подключения
            @self.client.on("connect")
            async def on_connect(_: ConnectEvent):
                self.is_monitoring = True
                self.is_processing = False
            
            # Обработчик отключения
            @self.client.on("disconnect")
            async def on_disconnect(event: DisconnectEvent):
                self.is_monitoring = False
                self.is_processing = False
                
            # Обработчик подарков
            @self.client.on("gift")
            async def on_gift(event: GiftEvent):
                # Создаем запись о событии
                item = TableItemView(
                    timestamp=datetime.now(),
                    name=event.user.nickname,
                    event=f"донат {event.gift.name}",
                    alert_level=AlertLevel.IMPORTANT
                )
                
                # Добавляем в список для UI
                self.add_item(item)
                
                # Озвучиваем и проигрываем звук, если включено
                if self.speech_gift:
                    self.speech_service.speech(
                        f"{event.user.nickname} прислал {event.gift.name}",
                        self.settings.speech_voice,
                        self.settings.speech_rate
                    )
                
                if self.notify_gift:
                    self.sound_service.play(event.gift.id, self.settings.notify_delay)
            
            # Обработчик лайков
            @self.client.on("like")
            async def on_like(event: LikeEvent):
                # Создаем запись о событии
                item = TableItemView(
                    timestamp=datetime.now(),
                    name=event.user.nickname,
                    event="лайк",
                    alert_level=AlertLevel.NORMAL
                )
                
                # Добавляем в список для UI
                self.add_item(item)
                
                # Озвучиваем, если включено
                if self.speech_like:
                    like_text = self.settings.like_text.replace("@name", event.user.nickname)
                    self.speech_service.speech(
                        like_text,
                        self.settings.speech_voice,
                        self.settings.speech_rate
                    )
            
            # Обработчик новых участников
            @self.client.on("join")
            async def on_join(event: JoinEvent):
                # Создаем запись о событии
                item = TableItemView(
                    timestamp=datetime.now(),
                    name=event.user.nickname,
                    event="подключение",
                    alert_level=AlertLevel.NORMAL
                )
                
                # Добавляем в список для UI
                self.add_item(item)
                
                # Озвучиваем, если включено
                if self.speech_member:
                    join_text = self.settings.join_text.replace("@name", event.user.nickname)
                    self.speech_service.speech(
                        join_text,
                        self.settings.speech_voice,
                        self.settings.speech_rate
                    )
            
            # Запускаем клиент и ждем завершения
            self.client_task = self.loop.create_task(self.client.start())
            self.loop.run_until_complete(self.client_task)
        
        except Exception as e:
            print(f"Ошибка при подключении к TikTok: {e}")
            self.is_monitoring = False
            self.is_processing = False
        
        finally:
            # Закрываем клиент и loop при завершении
            if self.client and self.client.connected:
                self.loop.run_until_complete(self.client.stop())
            
            if self.loop and self.loop.is_running():
                self.loop.close()
    
    def stop_monitoring(self):
        """Останавливает мониторинг стрима"""
        if self.client and self.client.connected:
            asyncio.run_coroutine_threadsafe(self.client.stop(), self.loop)
        
        self.is_monitoring = False