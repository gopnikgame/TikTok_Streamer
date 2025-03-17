from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QCheckBox, QComboBox, QSlider, QSpinBox, QMessageBox
from PyQt6.QtCore import Qt
from models.data_models import AlertLevel, TableItemView, GiftData
from utils.error_handler import ErrorHandler
from utils.logger import Logger
from PyQt6 import sip
from datetime import datetime
import asyncio

class SettingsTab(QWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.error_handler = ErrorHandler()
        self.logger = Logger().get_logger('SettingsTab')
        self.logger.info("Инициализация вкладки настроек")
        self.init_ui()
        self.bind_events()
        self.logger.debug("Вкладка настроек инициализирована")

    def init_ui(self):
        """Инициализирует пользовательский интерфейс вкладки настроек"""
        try:
            layout = QVBoxLayout()
            # Голос
            voice_layout = QHBoxLayout()
            voice_layout.addWidget(QLabel("Голос:"))
            self.voice_combo = QComboBox()
            try:
                # Получаем список доступных голосов
                voices = self.viewmodel.speech_service.get_voices()
                self.voice_combo.addItem("") # Пустой вариант для значения по умолчанию
                self.voice_combo.addItems(voices)
                # Устанавливаем текущий голос, если он задан
                current_voice = self.viewmodel.settings.speech_voice
                if current_voice and current_voice in voices:
                    self.voice_combo.setCurrentText(current_voice)
            except Exception as e:
                self.logger.error(f"Ошибка получения списка голосов: {str(e)}", exc_info=True)
                self.error_handler.handle_file_error(self, e, "voices")
            voice_layout.addWidget(self.voice_combo, 1)
            layout.addLayout(voice_layout)
            self.logger.debug("Создана строка для выбора голоса")
            # Скорость речи
            rate_layout = QHBoxLayout()
            rate_layout.addWidget(QLabel("Скорость речи:"))
            self.rate_slider = QSlider(Qt.Orientation.Horizontal)
            self.rate_slider.setRange(-10, 10)
            self.rate_slider.setValue(self.viewmodel.settings.speech_rate)
            rate_layout.addWidget(self.rate_slider, 1)
            layout.addLayout(rate_layout)
            self.logger.debug("Создана строка для скорости речи")
            # Громкость речи
            volume_layout = QHBoxLayout()
            volume_layout.addWidget(QLabel("Громкость речи:"))
            self.volume_slider = QSlider(Qt.Orientation.Horizontal)
            self.volume_slider.setRange(0, 100)  # Диапазон 0-100 для удобства пользователя
            self.volume_slider.setValue(int(self.viewmodel.settings.speech_volume * 100))  # Преобразуем из 0.0-1.0 в 0-100
            volume_layout.addWidget(self.volume_slider, 1)
            layout.addLayout(volume_layout)
            self.logger.debug("Создана строка для громкости речи")
            # Текст для подключения
            join_layout = QHBoxLayout()
            join_layout.addWidget(QLabel("Текст для подключения:"))
            self.join_text_input = QLineEdit()
            self.join_text_input.setText(self.viewmodel.settings.join_text)
            join_layout.addWidget(self.join_text_input, 1)
            layout.addLayout(join_layout)
            self.logger.debug("Создана строка для текста подключения")
            # Текст для лайка
            like_layout = QHBoxLayout()
            like_layout.addWidget(QLabel("Текст для лайка:"))
            self.like_text_input = QLineEdit()
            self.like_text_input.setText(self.viewmodel.settings.like_text)
            like_layout.addWidget(self.like_text_input, 1)
            layout.addLayout(like_layout)
            self.logger.debug("Создана строка для текста лайка")
            # Задержка звуковых уведомлений
            delay_layout = QHBoxLayout()
            delay_layout.addWidget(QLabel("Задержка между звуковыми уведомлениями (мс):"))
            self.delay_input = QSpinBox()
            self.delay_input.setRange(0, 10000)
            self.delay_input.setSingleStep(100)
            self.delay_input.setValue(self.viewmodel.settings.notify_delay)
            delay_layout.addWidget(self.delay_input, 1)
            layout.addLayout(delay_layout)
            self.logger.debug("Создана строка для задержки звуковых уведомлений")
            # Уровень логирования
            log_level_layout = QHBoxLayout()
            log_level_layout.addWidget(QLabel("Уровень логирования:"))
            self.log_level_combo = QComboBox()
            self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
            self.log_level_combo.setCurrentText(self.viewmodel.settings.logging_level)
            log_level_layout.addWidget(self.log_level_combo, 1)
            layout.addLayout(log_level_layout)
            self.logger.debug("Создана строка для уровня логирования")
            # Сохранение TikTok ID
            user_id_layout = QHBoxLayout()
            user_id_layout.addWidget(QLabel("ID стрима:"))
            self.user_id_combo = QComboBox()
            self.user_id_combo.addItems(self.viewmodel.settings.saved_user_ids)
            self.user_id_combo.setEditable(True)
            self.user_id_combo.setCurrentText(self.viewmodel.stream)
            user_id_layout.addWidget(self.user_id_combo, 1)
            layout.addLayout(user_id_layout)
            self.logger.debug("Создана строка для выбора/ввода ID стрима")
            # Кнопка сохранения
            save_btn = QPushButton("Сохранить настройки")
            save_btn.clicked.connect(self.save_settings)
            layout.addWidget(save_btn)
            layout.addStretch(1)
            self.setLayout(layout)
        except Exception as e:
            self.logger.error(f"Ошибка при создании вкладки настроек: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка создания интерфейса", 
                                              "Не удалось создать вкладку настроек", str(e))

    def bind_events(self):
        """Привязывает обработчики событий к изменениям ViewModel"""
        try:
            self.log_level_combo.currentIndexChanged.connect(self.update_logging_level)
            self.user_id_combo.currentIndexChanged.connect(self.update_user_id)
            self.rate_slider.valueChanged.connect(self.update_speech_rate)
            self.volume_slider.valueChanged.connect(self.update_speech_volume)
            self.logger.debug("Обработчики событий привязаны")
        except Exception as e:
            self.logger.error(f"Ошибка при привязке обработчиков событий: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка инициализации", 
                                             "Не удалось привязать обработчики событий", str(e))

    def update_logging_level(self, index):
        """Обновляет уровень логирования"""
        try:
            new_level = self.log_level_combo.currentText()
            self.viewmodel.settings.logging_level = new_level
            self.logger.setLevel(new_level)
            self.logger.debug(f"Уровень логирования изменен: {new_level}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении уровня логирования: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                                 "Не удалось изменить уровень логирования", str(e))

    def update_user_id(self, index):
        """Обновляет выбранный TikTok ID"""
        try:
            new_user_id = self.user_id_combo.currentText()
            if new_user_id not in self.viewmodel.settings.saved_user_ids:
                self.viewmodel.settings.saved_user_ids.append(new_user_id)
                asyncio.run(self.viewmodel.settings.save())  # Сохраняем новые ID стрима
            self.viewmodel.stream = new_user_id
            self.logger.debug(f"TikTok ID изменен: {new_user_id}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении TikTok ID: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                                 "Не удалось изменить TikTok ID", str(e))

    def update_speech_rate(self, value):
        """Обновляет скорость речи"""
        try:
            self.viewmodel.settings.speech_rate = value
            self.logger.debug(f"Скорость речи изменена: {value}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении скорости речи: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                                 "Не удалось изменить скорость речи", str(e))

    def update_speech_volume(self, value):
        """Обновляет громкость речи"""
        try:
            volume = value / 100.0  # Преобразуем из 0-100 в 0.0-1.0
            self.viewmodel.settings.speech_volume = volume
            self.viewmodel.speech_service.set_volume(volume)
            self.logger.debug(f"Громкость речи изменена: {volume}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении громкости речи: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                                 "Не удалось изменить громкость речи", str(e))

    def save_settings(self):
        """Сохраняет настройки"""
        try:
            # Валидация данных
            if self.join_text_input.text().strip() == "":
                self.error_handler.show_validation_error(self, "Текст для подключения не может быть пустым")
                return
            if self.like_text_input.text().strip() == "":
                self.error_handler.show_validation_error(self, "Текст для лайка не может быть пустым")
                return
            # Голос
            selected_voice = self.voice_combo.currentText()
            if selected_voice:
                self.viewmodel.settings.speech_voice = selected_voice
            # Скорость речи
            self.viewmodel.settings.speech_rate = self.rate_slider.value()
            # Громкость речи
            self.viewmodel.settings.speech_volume = self.volume_slider.value() / 100.0
            # Тексты
            self.viewmodel.settings.join_text = self.join_text_input.text()
            self.viewmodel.settings.like_text = self.like_text_input.text()
            # Задержка звуковых уведомлений
            self.viewmodel.settings.notify_delay = self.delay_input.value()
            # Сохраняем настройки
            asyncio.run(self.viewmodel.settings.save())
            self.logger.info("Настройки успешно сохранены")
            QMessageBox.information(self, "Настройки", "Настройки успешно сохранены")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении настроек: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка сохранения настроек", 
                                                 "Не удалось сохранить настройки", str(e))
