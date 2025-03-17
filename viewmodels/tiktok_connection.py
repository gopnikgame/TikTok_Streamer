from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, DisconnectEvent, CommentEvent, LikeEvent, GiftEvent, JoinEvent
from models.data_models import TableItemView, AlertLevel
from utils.logger import Logger
from PyQt6.QtCore import QObject, pyqtSignal
from datetime import datetime

class TikTokConnection(QObject):
    status_changed = pyqtSignal(str)
    item_added = pyqtSignal(TableItemView)

    def __init__(self, unique_id, settings, speech_service, sound_service, gift_service):
        super().__init__()
        self.logger = Logger().get_logger('TikTokConnection')
        self.logger.info("Инициализация TikTokConnection")
        self.unique_id = unique_id
        self.settings = settings
        self.speech_service = speech_service
        self.sound_service = sound_service
        self.gift_service = gift_service
        self.client = TikTokLiveClient(unique_id=self.unique_id)

        # Подключаем обработчики событий
        self.client.on(ConnectEvent)(self.on_connect)
        self.client.on(DisconnectEvent)(self.on_disconnect)
        self.client.on(CommentEvent)(self.on_comment)
        self.client.on(LikeEvent)(self.on_like)
        self.client.on(GiftEvent)(self.on_gift)
        self.client.on(JoinEvent)(self.on_join)

    async def on_connect(self, event: ConnectEvent):
        self.logger.info(f"Подключено к @{event.unique_id} (Room ID: {self.client.room_id})")
        self.status_changed.emit("Мониторинг активен")
        item = TableItemView(
            timestamp=datetime.now(),
            name="Система",
            event=f"Подключено к стриму @{event.unique_id}",
            alert_level=AlertLevel.NORMAL
        )
        self.item_added.emit(item)

    async def on_disconnect(self, event: DisconnectEvent):
        self.logger.info(f"Отключено от @{self.unique_id}")
        self.status_changed.emit("Мониторинг остановлен")
        item = TableItemView(
            timestamp=datetime.now(),
            name="Система",
            event=f"Отключено от стрима @{self.unique_id}",
            alert_level=AlertLevel.NORMAL
        )
        self.item_added.emit(item)

    async def on_comment(self, event: CommentEvent):
        self.logger.info(f"{event.user.nickname} -> {event.comment}")
        item = TableItemView(
            timestamp=datetime.now(),
            name=event.user.nickname,
            event=event.comment,
            alert_level=AlertLevel.NORMAL
        )
        self.item_added.emit(item)

    async def on_like(self, event: LikeEvent):
        self.logger.info(f"Получен лайк от {event.user.nickname}")
        item = TableItemView(
            timestamp=datetime.now(),
            name=event.user.nickname,
            event="Лайк",
            alert_level=AlertLevel.NORMAL
        )
        self.item_added.emit(item)

    async def on_gift(self, event: GiftEvent):
        self.logger.info(f"Получен подарок {event.gift.name} от {event.user.nickname}")
        item = TableItemView(
            timestamp=datetime.now(),
            name=event.user.nickname,
            event=f"Подарок: {event.gift.name}",
            alert_level=AlertLevel.IMPORTANT
        )
        self.item_added.emit(item)

    async def on_join(self, event: JoinEvent):
        self.logger.info(f"Новое подключение: {event.user.nickname}")
        item = TableItemView(
            timestamp=datetime.now(),
            name=event.user.nickname,
            event="Подключение",
            alert_level=AlertLevel.NORMAL
        )
        self.item_added.emit(item)

    def start(self):
        self.logger.info("Запуск клиента TikTok Live")
        self.client.run()

    async def stop(self):
        self.logger.info("Остановка клиента TikTok Live")
        await self.client.disconnect()