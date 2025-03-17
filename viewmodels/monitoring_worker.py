# monitoring_worker.py
import asyncio
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent, LikeEvent, JoinEvent, ConnectEvent, DisconnectEvent
from models.data_models import TableItemView, AlertLevel
from utils.settings import Settings
from utils.logger import Logger
from utils.error_handler import ErrorHandler
from PyQt6.QtCore import QObject, pyqtSignal
from datetime import datetime, timedelta

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
        self.client = None
        self.client_task = None
        self.loop = None
        self.is_monitoring = False
        self.is_processing = False
        self._shutdown_requested = False
        self.last_connect_time = None
        self.update_interval = 5.0  # Интервал обновления данных в секундах
        self.last_update_time = None

    def run(self):
        self.logger.debug("Запуск метода run в MonitoringWorker")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._run_tiktok_client())
        except asyncio.CancelledError:
            self.logger.debug("Работа была отменена")
        except Exception as e:
            self.logger.error(f"Ошибка в основном цикле: {str(e)}", exc_info=True)

    async def request_shutdown(self):
        """
        Безопасный метод для запроса завершения работы
        """
        self.logger.debug("Получен запрос на завершение работы")
        self._shutdown_requested = True
        if self.client and self.client.connected:
            try:
                self.logger.debug("Отключение клиента TikTok")
                await asyncio.wait_for(self.client.disconnect(), timeout=2.0)
            except (asyncio.TimeoutError, Exception) as e:
                self.logger.warning(f"Проблема при отключении клиента: {str(e)}")
        if self.client_task and not self.client_task.done():
            self.logger.debug("Отмена задачи клиента")
            self.client_task.cancel()
        return True  # Сигнализируем об успешной обработке запроса

    async def _run_tiktok_client(self):
        self.logger.debug("Запуск метода _run_tiktok_client")
        try:
            self.loop = asyncio.get_event_loop()
            max_retries = 5
            retry_count = 0
            retry_delay = 5  # начальная задержка в секундах
            max_delay = 300  # максимальная задержка в секундах

            while retry_count < max_retries and not self._shutdown_requested:
                try:
                    self.client = TikTokLiveClient(self.stream)
                    @self.client.on(ConnectEvent)
                    async def on_connect(event: ConnectEvent):
                        self.logger.info(f"Подключено к стриму {self.stream}")
                        self.is_monitoring = True
                        self.is_processing = False
                        current_time = datetime.now()
                        if self.last_connect_time is None or current_time - self.last_connect_time > timedelta(seconds=10):
                            item = TableItemView(
                                timestamp=current_time,
                                name="Система",
                                event=f"Подключено к стриму {self.stream}",
                                alert_level=AlertLevel.NORMAL
                            )
                            self.item_added.emit(item)
                            self.status_changed.emit("Мониторинг активен")
                            self.last_connect_time = current_time
                        else:
                            self.logger.warning(f"Игнорируем повторное событие подключения менее чем через 10 секунд")

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
                        await self._handle_event_with_throttle(event, "донат", AlertLevel.IMPORTANT)

                    @self.client.on(LikeEvent)
                    async def on_like(event: LikeEvent):
                        self.logger.debug(f"Получен лайк от {event.user.nickname}")
                        await self._handle_event_with_throttle(event, "лайк", AlertLevel.NORMAL)

                    @self.client.on(JoinEvent)
                    async def on_join(event: JoinEvent):
                        self.logger.debug(f"Новое подключение: {event.user.nickname}")
                        await self._handle_event_with_throttle(event, "подключение", AlertLevel.NORMAL)

                    self.logger.info("Запуск клиента TikTok Live")
                    self.client_task = self.loop.create_task(self.client.start())
                    while not self.client_task.done() and not self.client_task.cancelled() and not self._shutdown_requested:
                        await asyncio.sleep(1)
                        if not self.client.connected and not self._shutdown_requested:
                            self.logger.warning("Соединение с TikTok было разорвано")
                            break
                except asyncio.CancelledError:
                    self.logger.debug("Асинхронная задача была отменена")
                    break
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
                    retry_count += 1
                    delay = min(retry_delay * (2 ** retry_count), max_delay)
                    self.logger.warning(f"Попытка переподключения ({retry_count}/{max_retries}) через {delay} секунд")
                    await asyncio.sleep(delay)
        except asyncio.CancelledError:
            self.logger.debug("Асинхронная задача была отменена")
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
                    await asyncio.wait_for(self.client.disconnect(), timeout=1.0)
                except (asyncio.TimeoutError, Exception) as e:
                    self.logger.warning(f"Не удалось корректно закрыть клиент TikTok: {str(e)}")
            if self.loop and self.loop.is_running():
                try:
                    self.logger.debug("Очистка асинхронных генераторов")
                    await asyncio.wait_for(self.loop.shutdown_asyncgens(), timeout=1.0)
                except (asyncio.TimeoutError, Exception) as e:
                    self.logger.warning(f"Не удалось корректно закрыть асинхронные генераторы: {str(e)}")
            self.logger.debug("Завершение метода _run_tiktok_client")

    async def _handle_event_with_throttle(self, event, event_type, alert_level):
        current_time = datetime.now()
        if self.last_update_time is None or current_time - self.last_update_time > timedelta(seconds=self.update_interval):
            item = TableItemView(
                timestamp=current_time,
                name=event.user.nickname,
                event=event_type,
                alert_level=alert_level
            )
            self.item_added.emit(item)
            self.last_update_time = current_time
            if event_type == "донат":
                tasks = []
                if event.gift.streakable:
                    if not event.streaking:
                        if self.settings.speech_gift:
                            tasks.append(self.speech_service.speech(
                                f"{event.user.nickname} прислал {event.gift.name} {event.repeat_count} раз",
                                self.settings.speech_voice,
                                self.settings.speech_rate
                            ))
                        if self.settings.notify_gift:
                            tasks.append(self.sound_service.play(event.gift.id, self.settings.notify_delay))
                else:
                    if self.settings.speech_gift:
                        tasks.append(self.speech_service.speech(
                            f"{event.user.nickname} прислал {event.gift.name}",
                            self.settings.speech_voice,
                            self.settings.speech_rate
                        ))
                    if self.settings.notify_gift:
                        tasks.append(self.sound_service.play(event.gift.id, self.settings.notify_delay))
                await asyncio.gather(*tasks)
            elif event_type == "лайк":
                if self.settings.speech_like:
                    like_text = self.settings.like_text.replace("@name", event.user.nickname)
                    await self.speech_service.speech(
                        like_text,
                        self.settings.speech_voice,
                        self.settings.speech_rate
                    )
            elif event_type == "подключение":
                if self.settings.speech_member:
                    join_text = self.settings.join_text.replace("@name", event.user.nickname)
                    await self.speech_service.speech(
                        join_text,
                        self.settings.speech_voice,
                        self.settings.speech_rate
                    )
        else:
            self.logger.debug(f"Пропуск события {event_type} из-за ограничения частоты обновления")
