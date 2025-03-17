from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QSpinBox, QListView, QAbstractItemView, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6 import sip
from models.data_models import AlertLevel, TableItemView, GiftData
from utils.error_handler import ErrorHandler
from utils.logger import Logger
from datetime import datetime
import os
import shutil

class SoundsTab(QWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.error_handler = ErrorHandler()
        self.logger = Logger().get_logger('SoundsTab')
        self.logger.info("Инициализация вкладки звуков")
        self.init_ui()
        self.bind_events()
        self.update_sounds_list()
        self.update_mappings_list()
        self.logger.debug("Вкладка звуков инициализирована")

    def init_ui(self):
        """Инициализирует пользовательский интерфейс вкладки звуков"""
        try:
            layout = QVBoxLayout()
            # Панель для загрузки звуков
            upload_layout = QHBoxLayout()
            upload_btn = QPushButton("Загрузить звук")
            upload_btn.clicked.connect(self.upload_sound)
            upload_layout.addWidget(upload_btn)
            upload_layout.addStretch(1)
            layout.addLayout(upload_layout)
            self.logger.debug("Создана панель для загрузки звуков")
            # Список доступных звуков
            layout.addWidget(QLabel("Доступные звуки:"))
            self.sounds_model = QStandardItemModel()
            self.sounds_list = QListView()
            self.sounds_list.setModel(self.sounds_model)
            self.sounds_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            layout.addWidget(self.sounds_list)
            self.logger.debug("Создан список доступных звуков")
            # Привязка звуков к ID подарков
            layout.addWidget(QLabel("Привязка звуков к ID подарков:"))
            mapping_layout = QHBoxLayout()
            self.gift_id_input = QSpinBox()
            self.gift_id_input.setRange(1, 999999)
            self.sound_combo = QComboBox()
            self.add_mapping_btn = QPushButton("Добавить")
            self.add_mapping_btn.clicked.connect(self.add_sound_mapping)
            mapping_layout.addWidget(QLabel("ID подарка:"))
            mapping_layout.addWidget(self.gift_id_input)
            mapping_layout.addWidget(QLabel("Звук:"))
            mapping_layout.addWidget(self.sound_combo, 1)
            mapping_layout.addWidget(self.add_mapping_btn)
            layout.addLayout(mapping_layout)
            self.logger.debug("Создана панель для привязки звуков к ID подарков")
            # Список привязок звуков
            layout.addWidget(QLabel("Текущие привязки:"))
            self.mappings_model = QStandardItemModel()
            self.mappings_list = QListView()
            self.mappings_list.setModel(self.mappings_model)
            self.mappings_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            layout.addWidget(self.mappings_list)
            self.logger.debug("Создан список привязок звуков")
            self.setLayout(layout)
        except Exception as e:
            self.logger.error(f"Ошибка при создании вкладки звуков: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка создания интерфейса", 
                                              "Не удалось создать вкладку звуков", str(e))

    def bind_events(self):
        """Привязывает обработчики событий к изменениям ViewModel"""
        try:
            self.logger.debug("Обработчики событий привязаны")
        except Exception as e:
            self.logger.error(f"Ошибка при привязке обработчиков событий: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка инициализации", 
                                             "Не удалось привязать обработчики событий", str(e))

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
