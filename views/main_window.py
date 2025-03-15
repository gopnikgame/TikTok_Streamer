import os
import threading
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, 
    QTabWidget, QLineEdit, QLabel, QCheckBox, QComboBox, QSlider, QSpinBox,
    QListView, QAbstractItemView, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6 import sip
from models.data_models import AlertLevel
from utils.error_handler import ErrorHandler
from utils.logger import Logger

class EventsTableModel(QAbstractTableModel):
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel
        self.headers = ["Время", "Пользователь", "Событие"]
        self.logger = Logger().get_logger('EventsTableModel')
        self.logger.info("Инициализация модели таблицы событий")

    def rowCount(self, parent=None):
        self.logger.debug(f"Запрос количества строк: {len(self.viewmodel.item_list)}")
        return len(self.viewmodel.item_list)

    def columnCount(self, parent=None):
        self.logger.debug(f"Запрос количества столбцов: {len(self.headers)}")
        return 3

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.viewmodel.item_list)):
            self.logger.debug(f"Неверный индекс: {index}")
            return None
        item = self.viewmodel.item_list[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                self.logger.debug(f"Запрос данных для строки {index.row()}, столбца {index.column()}: {item.timestamp.strftime('%H:%M:%S')}")
                return item.timestamp.strftime("%H:%M:%S")
            elif index.column() == 1:
                self.logger.debug(f"Запрос данных для строки {index.row()}, столбца {index.column()}: {item.name}")
                return item.name
            elif index.column() == 2:
                self.logger.debug(f"Запрос данных для строки {index.row()}, столбца {index.column()}: {item.event}")
                return item.event
        elif role == Qt.ItemDataRole.BackgroundRole:
            if item.alert_level == AlertLevel.IMPORTANT:
                self.logger.debug(f"Запрос фона для строки {index.row()} с уровнем важности: {item.alert_level}")
                return Qt.GlobalColor.yellow
        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            self.logger.debug(f"Запрос заголовка для секции {section}: {self.headers[section]}")
            return self.headers[section]
        return None

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
            tabs = QTabWidget()
            tabs.addTab(self.create_monitoring_tab(), "Мониторинг")
            tabs.addTab(self.create_settings_tab(), "Настройки")
            tabs.addTab(self.create_sounds_tab(), "Звуки")
            # Устанавливаем основной виджет
            self.setCentralWidget(tabs)
            self.logger.debug("Интерфейс инициализирован")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации интерфейса: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка инициализации интерфейса", 
                                              "Не удалось инициализировать пользовательский интерфейс", str(e))

    def create_monitoring_tab(self):
        """Создает вкладку мониторинга"""
        try:
            tab = QWidget()
            layout = QVBoxLayout()
            # Строка с полем для ID стрима и кнопкой запуска
            stream_layout = QHBoxLayout()
            stream_label = QLabel("ID стрима:")
            self.stream_input = QLineEdit()
            self.stream_input.setText(self.viewmodel.stream)
            self.toggle_btn = QPushButton("Начать мониторинг")
            self.toggle_btn.clicked.connect(self.toggle_monitoring)
            stream_layout.addWidget(stream_label)
            stream_layout.addWidget(self.stream_input, 1)
            stream_layout.addWidget(self.toggle_btn)
            layout.addLayout(stream_layout)
            self.logger.debug("Создана строка для ID стрима и кнопки запуска")

            # Чекбоксы для настроек
            checks_layout = QHBoxLayout()
            self.notify_chk = QCheckBox("Звуковое оповещение")
            self.notify_chk.setChecked(self.viewmodel.notify_gift)
            self.notify_chk.clicked.connect(self.toggle_notify_gift)
            self.speech_gift_chk = QCheckBox("Озвучивать подарки")
            self.speech_gift_chk.setChecked(self.viewmodel.speech_gift)
            self.speech_gift_chk.clicked.connect(self.toggle_speech_gift)
            self.speech_like_chk = QCheckBox("Озвучивать лайки")
            self.speech_like_chk.setChecked(self.viewmodel.speech_like)
            self.speech_like_chk.clicked.connect(self.toggle_speech_like)
            self.speech_member_chk = QCheckBox("Озвучивать подключения")
            self.speech_member_chk.setChecked(self.viewmodel.speech_member)
            self.speech_member_chk.clicked.connect(self.toggle_speech_member)
            checks_layout.addWidget(self.notify_chk)
            checks_layout.addWidget(self.speech_gift_chk)
            checks_layout.addWidget(self.speech_like_chk)
            checks_layout.addWidget(self.speech_member_chk)
            layout.addLayout(checks_layout)
            self.logger.debug("Созданы чекбоксы для настроек")

            # Таблица событий
            self.table_model = EventsTableModel(self.viewmodel)
            self.table_view = QTableView()
            self.table_view.setModel(self.table_model)
            self.table_view.horizontalHeader().setStretchLastSection(True)
            layout.addWidget(self.table_view, 1)
            self.logger.debug("Создана таблица событий")

            # Статус
            self.status_label = QLabel("Статус: Готов к мониторингу")
            layout.addWidget(self.status_label)
            tab.setLayout(layout)
            self.logger.debug("Создана вкладка мониторинга")
            return tab
        except Exception as e:
            self.logger.error(f"Ошибка при создании вкладки мониторинга: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка создания интерфейса", 
                                              "Не удалось создать вкладку мониторинга", str(e))
            # В случае ошибки возвращаем пустой виджет
            return QWidget()

    def create_settings_tab(self):
        """Создает вкладку настроек"""
        try:
            tab = QWidget()
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

            # Кнопка сохранения
            save_btn = QPushButton("Сохранить настройки")
            save_btn.clicked.connect(self.save_settings)
            layout.addWidget(save_btn)
            layout.addStretch(1)
            tab.setLayout(layout)
            self.logger.debug("Создана вкладка настроек")
            return tab
        except Exception as e:
            self.logger.error(f"Ошибка при создании вкладки настроек: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка создания интерфейса", 
                                              "Не удалось создать вкладку настроек", str(e))
            # В случае ошибки возвращаем пустой виджет
            return QWidget()

    def create_sounds_tab(self):
        """Создает вкладку настройки звуков"""
        try:
            tab = QWidget()
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

            # Обновляем списки
            self.update_sounds_list()
            self.update_mappings_list()
            tab.setLayout(layout)
            self.logger.debug("Создана вкладка звуков")
            return tab
        except Exception as e:
            self.logger.error(f"Ошибка при создании вкладки звуков: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка создания интерфейса", 
                                              "Не удалось создать вкладку звуков", str(e))
            # В случае ошибки возвращаем пустой виджет
            return QWidget()

    def bind_events(self):
        """Привязывает обработчики событий к изменениям ViewModel"""
        try:
            self.viewmodel.add_callback('is_monitoring', self.update_monitoring_state)
            self.viewmodel.add_callback('item_list', self.update_events_table)
            self.logger.debug("Обработчики событий привязаны")
        except Exception as e:
            self.logger.error(f"Ошибка при привязке обработчиков событий: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка инициализации", 
                                             "Не удалось привязать обработчики событий", str(e))

    def update_monitoring_state(self):
        """Обновляет состояние интерфейса в зависимости от статуса мониторинга"""
        try:
            if self.viewmodel.is_processing:
                self.toggle_btn.setEnabled(False)
                self.status_label.setText("Статус: Подключение...")
                self.stream_input.setEnabled(False)
                self.logger.debug("Обновлено состояние: Подключение...")
            elif self.viewmodel.is_monitoring:
                self.toggle_btn.setText("Остановить мониторинг")
                self.toggle_btn.setEnabled(True)
                self.status_label.setText(f"Статус: Мониторинг стрима {self.viewmodel.stream}")
                self.stream_input.setEnabled(False)
                self.logger.debug(f"Обновлено состояние: Мониторинг стрима {self.viewmodel.stream}")
            else:
                self.toggle_btn.setText("Начать мониторинг")
                self.toggle_btn.setEnabled(True)
                self.status_label.setText("Статус: Готов к мониторингу")
                self.stream_input.setEnabled(True)
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
            stream = self.stream_input.text().strip()
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
            self.viewmodel.notify_gift = self.notify_chk.isChecked()
            self.logger.debug(f"Настройка звуковых оповещений изменена: {self.viewmodel.notify_gift}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении настройки звуковых оповещений: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                             "Не удалось изменить настройку звуковых оповещений", str(e))

    def toggle_speech_gift(self):
        """Включает или выключает озвучивание подарков"""
        try:
            self.viewmodel.speech_gift = self.speech_gift_chk.isChecked()
            self.logger.debug(f"Настройка озвучивания подарков изменена: {self.viewmodel.speech_gift}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении настройки озвучивания подарков: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                             "Не удалось изменить настройку озвучивания подарков", str(e))

    def toggle_speech_like(self):
        """Включает или выключает озвучивание лайков"""
        try:
            self.viewmodel.speech_like = self.speech_like_chk.isChecked()
            self.logger.debug(f"Настройка озвучивания лайков изменена: {self.viewmodel.speech_like}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении настройки озвучивания лайков: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                             "Не удалось изменить настройку озвучивания лайков", str(e))

    def toggle_speech_member(self):
        """Включает или выключает озвучивание подключений"""
        try:
            self.viewmodel.speech_member = self.speech_member_chk.isChecked()
            self.logger.debug(f"Настройка озвучивания подключений изменена: {self.viewmodel.speech_member}")
        except Exception as e:
            self.logger.error(f"Ошибка при изменении настройки озвучивания подключений: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "Ошибка настроек", 
                                             "Не удалось изменить настройку озвучивания подключений", str(e))

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
            # Тексты
            self.viewmodel.settings.join_text = self.join_text_input.text()
            self.viewmodel.settings.like_text = self.like_text_input.text()
            # Задержка звуковых уведомлений
            self.viewmodel.settings.notify_delay = self.delay_input.value()
            # Сохраняем настройки
            self.viewmodel.settings.save()
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