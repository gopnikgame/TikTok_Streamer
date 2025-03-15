import asyncio
import threading
from datetime import datetime
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent, LikeEvent, JoinEvent, ConnectEvent, DisconnectEvent
from models.data_models import TableItemView, AlertLevel
from utils.settings import Settings
from utils.logger import Logger
from utils.error_handler import ErrorHandler

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
        self.notify_property_changed('item_list')
        # Запускаем клиент TikTok в отдельном потоке
        threading.Thread(target=self._run_tiktok_client, daemon=True).start()

    def stop_monitoring(self):
        """Останавливает мониторинг стрима"""
        if self.client and self.client.connected:
            try:
                self.logger.info("Остановка мониторинга стрима")
                asyncio.run_coroutine_threadsafe(self.client.stop(), self.loop)
            except Exception as e:
                self.logger.error(f"Ошибка при остановке клиента: {str(e)}")
                self.error_handler.handle_tiktok_error(None, e)
        self.is_monitoring = False
        self.logger.info("Мониторинг остановлен")

    def _run_tiktok_client(self):
        """Запускает клиент TikTok Live в отдельном потоке"""
        self.logger.debug("Запуск метода _run_tiktok_client")
        try:
            self.logger.debug("Создание нового event loop для TikTok клиента")
            # Создаем новый event loop для асинхронного кода
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.logger.debug(f"Создан новый event loop: {self.loop}")
            # Создаем клиент и регистрируем обработчики событий
            self.logger.debug(f"Инициализация TikTokLiveClient для {self.stream}")
            self.client = TikTokLiveClient(self.stream)
            self.logger.debug(f"TikTokLiveClient создан: {self.client}")

            # Обработчик подключения
            @self.client.on(ConnectEvent)
            async def on_connect(event: ConnectEvent):
                self.logger.info(f"Подключено к стриму {self.stream}")
                self.is_monitoring = True
                self.is_processing = False
                # Добавляем событие о подключении
                item = TableItemView(
                    timestamp=datetime.now(),
                    name="Система",
                    event=f"Подключено к стриму {self.stream}",
                    alert_level=AlertLevel.NORMAL
                )
                self.add_item(item)
                self.logger.debug("on_connect обработчик завершен")

            # Обработчик отключения
            @self.client.on(DisconnectEvent)
            async def on_disconnect(event: DisconnectEvent):
                self.logger.info(f"Отключено от стрима {self.stream}")
                self.is_monitoring = False
                self.is_processing = False
                # Добавляем событие об отключении
                item = TableItemView(
                    timestamp=datetime.now(),
                    name="Система",
                    event=f"Отключено от стрима {self.stream}",
                    alert_level=AlertLevel.NORMAL
                )
                self.add_item(item)
                self.logger.debug("on_disconnect обработчик завершен")

            # Обработчики подарков, лайков и подключений
            @self.client.on(GiftEvent)
            async def on_gift(event: GiftEvent):
                self.logger.info(f"Получен подарок {event.gift.name} от {event.user.nickname}")
                try:
                    if event.gift.streakable:
                        if not event.streaking:
                            item = TableItemView(
                                timestamp=datetime.now(),
                                name=event.user.nickname,
                                event=f"донат {event.gift.name} x{event.repeat_count}",
                                alert_level=AlertLevel.IMPORTANT
                            )
                            self.add_item(item)
                            if self.speech_gift:
                                self.logger.debug(f"Озвучивание подарка от {event.user.nickname}")
                                self.speech_service.speech(
                                    f"{event.user.nickname} прислал {event.gift.name} {event.repeat_count} раз",
                                    self.settings.speech_voice,
                                    self.settings.speech_rate
                                )
                            if self.notify_gift:
                                self.logger.debug(f"Воспроизведение звука для подарка ID {event.gift.id}")
                                self.sound_service.play(event.gift.id, self.settings.notify_delay)
                    else:
                        item = TableItemView(
                            timestamp=datetime.now(),
                            name=event.user.nickname,
                            event=f"донат {event.gift.name}",
                            alert_level=AlertLevel.IMPORTANT
                        )
                        self.add_item(item)
                        if self.speech_gift:
                            self.logger.debug(f"Озвучивание подарка от {event.user.nickname}")
                            self.speech_service.speech(
                                f"{event.user.nickname} прислал {event.gift.name}",
                                self.settings.speech_voice,
                                self.settings.speech_rate
                            )
                        if self.notify_gift:
                            self.logger.debug(f"Воспроизведение звука для подарка ID {event.gift.id}")
                            self.sound_service.play(event.gift.id, self.settings.notify_delay)
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
                    self.add_item(item)
                    if self.speech_like:
                        like_text = self.settings.like_text.replace("@name", event.user.nickname)
                        self.logger.debug(f"Озвучивание лайка: {like_text}")
                        self.speech_service.speech(
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
                    self.add_item(item)
                    if self.speech_member:
                        join_text = self.settings.join_text.replace("@name", event.user.nickname)
                        self.logger.debug(f"Озвучивание подключения: {join_text}")
                        self.speech_service.speech(
                            join_text,
                            self.settings.speech_voice,
                            self.settings.speech_rate
                        )
                except Exception as e:
                    self.logger.error(f"Ошибка при обработке подключения: {str(e)}", exc_info=True)

            # Запускаем клиент и ждем завершения
            self.logger.info("Запуск клиента TikTok Live")
            self.client_task = self.loop.create_task(self.client.start())
            self.logger.debug(f"Задача клиента создана: {self.client_task}")
            while True:
                self.logger.debug(f"Состояние клиента: {self.client.connected}")
                await asyncio.sleep(5)  # Проверяем состояние каждые 5 секунд
        except Exception as e:
            self.logger.error(f"Ошибка при подключении к TikTok: {str(e)}", exc_info=True)
            item = TableItemView(
                timestamp=datetime.now(),
                name="Система",
                event=f"Ошибка: {str(e)}",
                alert_level=AlertLevel.IMPORTANT
            )
            self.add_item(item)
            self.error_handler.handle_tiktok_error(None, e)
            self.is_monitoring = False
            self.is_processing = False
        finally:
            self.logger.debug("Выполнение блока finally в методе _run_tiktok_client")
            if self.client and self.client.connected:
                try:
                    self.logger.debug("Закрытие клиента TikTok")
                    self.loop.run_until_complete(self.client.stop())
                except Exception as e:
                    self.logger.error(f"Ошибка при закрытии клиента TikTok: {str(e)}")
                    self.error_handler.show_error_dialog(None, "Ошибка", "Ошибка при закрытии клиента TikTok", str(e))
            if self.loop and self.loop.is_running():
                self.logger.debug("Закрытие event loop")
                try:
                    self.loop.run_until_complete(self.loop.shutdown_asyncgens())
                    self.loop.close()
                except Exception as e:
                    self.logger.error(f"Ошибка при закрытии event loop: {str(e)}")
                    self.error_handler.show_error_dialog(None, "Ошибка", "Ошибка при закрытии event loop", str(e))
            self.logger.debug("Завершение метода _run_tiktok_client")