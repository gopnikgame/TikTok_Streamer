# monitoring_worker.py
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
        self.client = None
        self.client_task = None
        self.loop = None
        self.is_monitoring = False
        self.is_processing = False
        self._shutdown_requested = False  # Новый флаг для отслеживания запроса на завершение

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
        # НЕ закрываем loop в finally, это должно происходить только через request_shutdown

    async def request_shutdown(self):
        """Безопасный метод для запроса завершения работы"""
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
            while retry_count < max_retries and not self._shutdown_requested:
                try:
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
                    # Основной цикл работы
                    while not self.client_task.done() and not self.client_task.cancelled() and not self._shutdown_requested:
                        await asyncio.sleep(1)  # Уменьшаем интервал для более быстрой реакции на shutdown
                        # Проверяем статус клиента во время выполнения
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
                    self.logger.warning(f"Попытка переподключения ({retry_count}/{max_retries})")
                    await asyncio.sleep(5)  # Пауза перед следующей попыткой
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
            # ⚠️ Аккуратно выполняем очистку без закрытия event loop
            self.logger.debug("Выполнение блока finally в методе _run_tiktok_client")
            # Отключаем клиента, если он всё ещё подключен
            if self.client and self.client.connected:
                try:
                    self.logger.debug("Закрытие клиента TikTok")
                    # Используем wait_for с небольшим таймаутом, чтобы не блокировать завершение
                    await asyncio.wait_for(self.client.disconnect(), timeout=1.0)
                except (asyncio.TimeoutError, Exception) as e:
                    self.logger.warning(f"Не удалось корректно закрыть клиент TikTok: {str(e)}")
            # Очищаем ресурсы без закрытия loop
            if self.loop and self.loop.is_running():
                try:
                    self.logger.debug("Очистка асинхронных генераторов")
                    # Используем небольшой таймаут для shutdown_asyncgens
                    await asyncio.wait_for(self.loop.shutdown_asyncgens(), timeout=1.0)
                except (asyncio.TimeoutError, Exception) as e:
                    self.logger.warning(f"Не удалось корректно закрыть асинхронные генераторы: {str(e)}")
            # НЕ останавливаем и не закрываем loop здесь!
            self.logger.debug("Завершение метода _run_tiktok_client")
