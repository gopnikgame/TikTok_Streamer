import asyncio
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent, LikeEvent, JoinEvent, ConnectEvent, DisconnectEvent
from models.data_models import TableItemView, AlertLevel
from utils.settings import Settings
from utils.logger import Logger
from utils.error_handler import ErrorHandler
from PyQt6.QtCore import QObject, pyqtSignal
from datetime import datetime

class MonitoringWorker(QObject):
    status_changed = pyqtSignal(str)
    item_added = pyqtSignal(TableItemView)

    def __init__(self, stream, settings, speech_service, sound_service, gift_service):
        super().__init__()
        self.logger = Logger().get_logger('MonitoringWorker')
        self.logger.info("Инициализация MonitoringWorker")
        self.stream = stream
        self.settings = settings
        self.speech_service = speech_service
        self.sound_service = sound_service
        self.gift_service = gift_service
        self.error_handler = ErrorHandler()
        self.client = TikTokLiveClient(self.stream)
        self.client_task = None
        self.loop = None
        self.is_monitoring = False
        self.is_processing = False

    def run(self):
        self.logger.debug("Запуск метода run в MonitoringWorker")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._run_tiktok_client())
        finally:
            loop.close()

    async def _run_tiktok_client(self):
        self.logger.debug("Запуск метода _run_tiktok_client")
        try:
            self.loop = asyncio.get_event_loop()
            self.client = TikTokLiveClient(self.stream)

            @self.client.on(ConnectEvent)
            async def on_connect(event: ConnectEvent):
                self.logger.info(f"Подключено к стриму {self.stream}")
                self.is_monitoring = True
                self.is_processing = False
                item = TableItemView(
                    timestamp=datetime.now(),
                    name="Система",
                    event=f"Подключено к стриму {self.stream}",
                    alert_level=AlertLevel.NORMAL
                )
                self.item_added.emit(item)
                self.status_changed.emit("Мониторинг активен")

            @self.client.on(DisconnectEvent)
            async def on_disconnect(event: DisconnectEvent):
                self.logger.info(f"Отключено от стрима {self.stream}")
                self.is_monitoring = False
                self.is_processing = False
                item = TableItemView(
                    timestamp=datetime.now(),
                    name="Система",
                    event=f"Отключено от стрима {self.stream}",
                    alert_level=AlertLevel.NORMAL
                )
                self.item_added.emit(item)
                self.status_changed.emit("Мониторинг остановлен")

            @self.client.on(GiftEvent)
            async def on_gift(event: GiftEvent):
                self.logger.info(f"Получен подарок {event.gift.name} от {event.user.nickname}")
                try:
                    tasks = []
                    if event.gift.streakable:
                        if not event.streaking:
                            item = TableItemView(
                                timestamp=datetime.now(),
                                name=event.user.nickname,
                                event=f"донат {event.gift.name} x{event.repeat_count}",
                                alert_level=AlertLevel.IMPORTANT
                            )
                            self.item_added.emit(item)
                            if self.settings.speech_gift:
                                tasks.append(self.speech_service.speech(
                                    f"{event.user.nickname} прислал {event.gift.name} {event.repeat_count} раз",
                                    self.settings.speech_voice,
                                    self.settings.speech_rate
                                ))
                            if self.settings.notify_gift:
                                tasks.append(self.sound_service.play(event.gift.id, self.settings.notify_delay))
                    else:
                        item = TableItemView(
                            timestamp=datetime.now(),
                            name=event.user.nickname,
                            event=f"донат {event.gift.name}",
                            alert_level=AlertLevel.IMPORTANT
                        )
                        self.item_added.emit(item)
                        if self.settings.speech_gift:
                            tasks.append(self.speech_service.speech(
                                f"{event.user.nickname} прислал {event.gift.name}",
                                self.settings.speech_voice,
                                self.settings.speech_rate
                            ))
                        if self.settings.notify_gift:
                            tasks.append(self.sound_service.play(event.gift.id, self.settings.notify_delay))
                    await asyncio.gather(*tasks)
                except Exception as e:
                    self.logger.error(f"Ошибка при обработке подарка: {str(e)}", exc_info=True)

            @self.client.on(LikeEvent)
            async def on_like(event: LikeEvent):
                self.logger.debug(f"Получен лайк от {event.user.nickname}")
                try:
                    item = TableItemView(
                        timestamp=datetime.now(),
                        name=event.user.nickname,
                        event="лайк",
                        alert_level=AlertLevel.NORMAL
                    )
                    self.item_added.emit(item)
                    if self.settings.speech_like:
                        like_text = self.settings.like_text.replace("@name", event.user.nickname)
                        await self.speech_service.speech(
                            like_text,
                            self.settings.speech_voice,
                            self.settings.speech_rate
                        )
                except Exception as e:
                    self.logger.error(f"Ошибка при обработке лайка: {str(e)}", exc_info=True)

            @self.client.on(JoinEvent)
            async def on_join(event: JoinEvent):
                self.logger.debug(f"Новое подключение: {event.user.nickname}")
                try:
                    item = TableItemView(
                        timestamp=datetime.now(),
                        name=event.user.nickname,
                        event="подключение",
                        alert_level=AlertLevel.NORMAL
                    )
                    self.item_added.emit(item)
                    if self.settings.speech_member:
                        join_text = self.settings.join_text.replace("@name", event.user.nickname)
                        await self.speech_service.speech(
                            join_text,
                            self.settings.speech_voice,
                            self.settings.speech_rate
                        )
                except Exception as e:
                    self.logger.error(f"Ошибка при обработке подключения: {str(e)}", exc_info=True)

            self.logger.info("Запуск клиента TikTok Live")
            self.client_task = self.loop.create_task(self.client.start())
            while not self.client_task.done() and not self.client_task.cancelled():
                await asyncio.sleep(5)
        except Exception as e:
            self.logger.error(f"Ошибка при подключении к TikTok: {str(e)}", exc_info=True)
            item = TableItemView(
                timestamp=datetime.now(),
                name="Система",
                event=f"Ошибка: {str(e)}",
                alert_level=AlertLevel.IMPORTANT
            )
            self.item_added.emit(item)
            self.error_handler.handle_tiktok_error(None, e)
            self.is_monitoring = False
            self.is_processing = False
        finally:
            self.logger.debug("Выполнение блока finally в методе _run_tiktok_client")
            if self.client and self.client.connected:
                try:
                    self.logger.debug("Закрытие клиента TikTok")
                    await self.client.disconnect()  # Используем метод disconnect вместо несуществующего stop
                except Exception as e:
                    self.logger.error(f"Ошибка при закрытии клиента TikTok: {str(e)}")
                    self.error_handler.show_error_dialog(None, "Ошибка", "Ошибка при закрытии клиента TikTok", str(e))
            if self.loop and self.loop.is_running():
                self.logger.debug("Закрытие event loop")
                try:
                    await self.loop.shutdown_asyncgens()
                    self.loop.stop()  # Останавливаем event loop
                except Exception as e:
                    self.logger.error(f"Ошибка при закрытии event loop: {str(e)}")
                    self.error_handler.show_error_dialog(None, "Ошибка", "Ошибка при закрытии event loop", str(e))
            self.logger.debug("Завершение метода _run_tiktok_client")