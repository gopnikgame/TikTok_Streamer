import os
import asyncio
import threading
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QFileDialog
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
from datetime import datetime
from .monitoring_tab import MonitoringTab
from .settings_tab import SettingsTab
from .sounds_tab import SoundsTab
from .events_table_model import EventsTableModel  # Импортируем EventsTableModel из отдельного файла

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
            self.tabs = QTabWidget()
            self.monitoring_tab = MonitoringTab(self.viewmodel, self)
            self.tabs.addTab(self.monitoring_tab, "Мониторинг")
            self.tabs.addTab(SettingsTab(self.viewmodel, self), "Настройки")
            self.tabs.addTab(SoundsTab(self.viewmodel, self), "Звуки")
            # Устанавливаем основной виджет
            self.setCentralWidget(self.tabs)
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
                self.monitoring_tab.toggle_btn.setEnabled(False)
                self.monitoring_tab.status_label.setText("Статус: Подключение...")
                self.monitoring_tab.stream_input.setEnabled(False)
                self.logger.debug("Обновлено состояние: Подключение...")
            elif self.viewmodel.is_monitoring:
                self.monitoring_tab.toggle_btn.setText("Остановить мониторинг")
                self.monitoring_tab.toggle_btn.setEnabled(True)
                self.monitoring_tab.status_label.setText(f"Статус: Мониторинг стрима {self.viewmodel.stream}")
                self.monitoring_tab.stream_input.setEnabled(False)
                self.logger.debug(f"Обновлено состояние: Мониторинг стрима {self.viewmodel.stream}")
            else:
                self.monitoring_tab.toggle_btn.setText("Начать мониторинг")
                self.monitoring_tab.toggle_btn.setEnabled(True)
                self.monitoring_tab.status_label.setText("Статус: Готов к мониторингу")
                self.monitoring_tab.stream_input.setEnabled(True)
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
    
    def toggle_monitoring(self):
        """Включает или выключает мониторинг"""
        try:
            if self.viewmodel.is_monitoring:
                self.logger.info("Остановка мониторинга")
                self.viewmodel.stop_monitoring()
                return
            # Получаем ID стрима из поля ввода
            stream = self.monitoring_tab.stream_input.text().strip()
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
            self.viewmodel.notify_gift = self.monitoring_tab.notify_chk.isChecked()
            self.logger.debug(f"Настройка звуковых оповещений изменена: {self.viewmodel.notify_gift}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении настройки звуковых оповещений: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                                 "Не удалось изменить настройку звуковых оповещений", str(e))
    
    def toggle_speech_gift(self):
        """Включает или выключает озвучивание подарков"""
        try:
            self.viewmodel.speech_gift = self.monitoring_tab.speech_gift_chk.isChecked()
            self.logger.debug(f"Настройка озвучивания подарков изменена: {self.viewmodel.speech_gift}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении настройки озвучивания подарков: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                                 "Не удалось изменить настройку озвучивания подарков", str(e))
    
    def toggle_speech_like(self):
        """Включает или выключает озвучивание лайков"""
        try:
            self.viewmodel.speech_like = self.monitoring_tab.speech_like_chk.isChecked()
            self.logger.debug(f"Настройка озвучивания лайков изменена: {self.viewmodel.speech_like}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении настройки озвучивания лайков: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                                 "Не удалось изменить настройку озвучивания лайков", str(e))
    
    def toggle_speech_member(self):
        """Включает или выключает озвучивание подключений"""
        try:
            self.viewmodel.speech_member = self.monitoring_tab.speech_member_chk.isChecked()
            self.logger.debug(f"Настройка озвучивания подключений изменена: {self.viewmodel.speech_member}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении настройки озвучивания подключений: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                                 "Не удалось изменить настройку озвучивания подключений", str(e))
    
    def save_settings(self):
        """Сохраняет настройки"""
        try:
            # Валидация данных
            if self.monitoring_tab.join_text_input.text().strip() == "":
                self.error_handler.show_validation_error(self, "Текст для подключения не может быть пустым")
                return
            if self.monitoring_tab.like_text_input.text().strip() == "":
                self.error_handler.show_validation_error(self, "Текст для лайка не может быть пустым")
                return
            # Голос
            selected_voice = self.monitoring_tab.voice_combo.currentText()
            if selected_voice:
                self.viewmodel.settings.speech_voice = selected_voice
            # Скорость речи
            self.viewmodel.settings.speech_rate = self.monitoring_tab.rate_slider.value()
            # Громкость речи
            self.viewmodel.settings.speech_volume = self.monitoring_tab.volume_slider.value() / 100.0
            # Тексты
            self.viewmodel.settings.join_text = self.monitoring_tab.join_text_input.text()
            self.viewmodel.settings.like_text = self.monitoring_tab.like_text_input.text()
            # Задержка звуковых уведомлений
            self.viewmodel.settings.notify_delay = self.monitoring_tab.delay_input.value()
            # Сохраняем настройки
            asyncio.run(self.viewmodel.settings.save())
            self.logger.info("Настройки успешно сохранены")
            QMessageBox.information(self, "Настройки", "Настройки успешно сохранены")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении настроек: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка сохранения настроек", 
                                                 "Не удалось сохранить настройки", str(e))
    
    def update_sounds_list(self):
        """Обновляет список доступных звуков"""
        try:
            self.sounds_model.clear()
            self.sound_combo.clear()
            if not os.path.exists("assets"):
                os.makedirs("assets")
                self.logger.info("Создана директория assets")
            # Получаем список звуковых файлов
            sound_files = [f for f in os.listdir("assets") if f.lower().endswith(('.mp3', '.wav'))]
            for sound in sound_files:
                self.sounds_model.appendRow(QStandardItem(sound))
                self.sound_combo.addItem(sound)
            self.logger.debug(f"Обновлен список звуков: {len(sound_files)} файлов")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении списка звуков: {str(e)}", exc_info=True)
            self.error_handler.handle_file_error(self, e, "assets")
    
    def update_mappings_list(self):
        """Обновляет список привязок звуков к ID подарков"""
        try:
            self.mappings_model.clear()
            # Получаем текущие привязки
            mappings = self.viewmodel.sound_service.get_mappings()
            for gift_id, sound_file in mappings.items():
                self.mappings_model.appendRow(
                    QStandardItem(f"ID {gift_id}: {sound_file}")
                )
            self.logger.debug(f"Обновлен список привязок: {len(mappings)} привязок")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении списка привязок: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка обновления списка", 
                                                 "Не удалось обновить список привязок", str(e))
    
    def upload_sound(self):
        """Загружает новый звуковой файл"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Выберите звуковой файл", "", "Аудио файлы (*.mp3 *.wav)"
            )
            if not file_path:
                return
            # Копируем файл в директорию assets
            file_name = os.path.basename(file_path)
            destination = os.path.join("assets", file_name)
            try:
                # Проверяем, существует ли директория assets
                if not os.path.exists("assets"):
                    os.makedirs("assets")
                # Копируем файл
                import shutil
                shutil.copy2(file_path, destination)
                self.logger.info(f"Звуковой файл загружен: {file_name}")
                # Обновляем списки
                self.update_sounds_list()
                QMessageBox.information(self, "Загрузка звука", f"Файл {file_name} успешно загружен")
            except Exception as e:
                self.logger.error(f"Ошибка при копировании звукового файла: {str(e)}", exc_info=True)
                self.error_handler.handle_file_error(self, e, destination)
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке звука: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка загрузки звука", 
                                                 "Не удалось загрузить звуковой файл", str(e))
    
    def add_sound_mapping(self):
        """Добавляет новую привязку звука к ID подарка"""
        try:
            gift_id = self.gift_id_input.value()
            sound_file = self.sound_combo.currentText()
            if not sound_file:
                self.error_handler.show_validation_error(self, "Пожалуйста, выберите звуковой файл")
                return
            # Добавляем привязку
            self.viewmodel.sound_service.add_mapping(gift_id, sound_file)
            self.logger.info(f"Добавлена привязка звука: ID {gift_id} -> {sound_file}")
            # Обновляем список привязок
            self.update_mappings_list()
            QMessageBox.information(
                self, 
                "Привязка звука", 
                f"Подарок с ID {gift_id} теперь будет сопровождаться звуком {sound_file}"
            )
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении привязки звука: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка привязки звука", 
                                                 "Не удалось привязать звук к ID подарка", str(e))
    
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
            self.monitoring_tab.status_label.setText(f"Статус: {status}")
            self.logger.info(f"Статус обновлен: {status}")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении статуса: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка обновления статуса", 
                                                 "Не удалось обновить статус", str(e))
