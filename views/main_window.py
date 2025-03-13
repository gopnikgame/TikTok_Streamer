import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QLabel, QLineEdit, QPushButton, QCheckBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt, QTimer

from viewmodels.monitoring_viewmodel import MonitoringViewModel
from models.data_models import AlertLevel

class MainWindow(QMainWindow):
    def __init__(self, monitoring_viewmodel):
        super().__init__()
        
        self.viewmodel = monitoring_viewmodel
        
        # Настраиваем главное окно
        self.setWindowTitle("TTStreamerPy")
        self.setMinimumSize(800, 600)
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        self.monitoring_tab = self.create_monitoring_tab()
        self.settings_tab = self.create_settings_tab()
        self.sound_tab = self.create_sound_tab()
        
        self.tabs.addTab(self.monitoring_tab, "Мониторинг")
        self.tabs.addTab(self.settings_tab, "Настройки")
        self.tabs.addTab(self.sound_tab, "Звуки")
        
        # Устанавливаем центральный виджет
        self.setCentralWidget(self.tabs)
        
        # Настраиваем обновление UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)  # Обновление каждые 100 мс
        
        # Настраиваем привязки данных
        self.bind_data()
    
    def create_monitoring_tab(self):
        """Создает вкладку мониторинга"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Виджеты для управления стримом
        controls_layout = QHBoxLayout()
        
        # Поле для ID стрима
        stream_label = QLabel("ID стрима:")
        self.stream_input = QLineEdit()
        controls_layout.addWidget(stream_label)
        controls_layout.addWidget(self.stream_input)
        
        # Кнопка мониторинга
        self.monitor_btn = QPushButton("Начать мониторинг")
        self.monitor_btn.clicked.connect(self.toggle_monitoring)
        controls_layout.addWidget(self.monitor_btn)
        
        layout.addLayout(controls_layout)
        
        # Настройки оповещений
        notify_layout = QHBoxLayout()
        
        self.notify_gift_chk = QCheckBox("Звуковое оповещение о донатах")
        self.speech_gift_chk = QCheckBox("Озвучивать донаты")
        self.speech_like_chk = QCheckBox("Озвучивать лайки")
        self.speech_member_chk = QCheckBox("Озвучивать подключения")
        
        notify_layout.addWidget(self.notify_gift_chk)
        notify_layout.addWidget(self.speech_gift_chk)
        notify_layout.addWidget(self.speech_like_chk)
        notify_layout.addWidget(self.speech_member_chk)
        
        layout.addLayout(notify_layout)
        
        # Таблица событий
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(3)
        self.events_table.setHorizontalHeaderLabels(["Время", "Пользователь", "Событие"])
        self.events_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.events_table)
        
        tab.setLayout(layout)
        return tab
    
    def create_settings_tab(self):
        """Создает вкладку настроек"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Настройки синтеза речи
        speech_group_layout = QVBoxLayout()
        speech_group_layout.addWidget(QLabel("Настройки синтеза речи"))
        
        # Выбор голоса
        voice_layout = QHBoxLayout()
        voice_label = QLabel("Голос:")
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(self.viewmodel.speech_service.get_voices())
        voice_layout.addWidget(voice_label)
        voice_layout.addWidget(self.voice_combo)
        speech_group_layout.addLayout(voice_layout)
        
        # Скорость речи
        rate_layout = QHBoxLayout()
        rate_label = QLabel("Скорость речи:")
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setMinimum(-10)
        self.rate_slider.setMaximum(10)
        self.rate_slider.setValue(self.viewmodel.settings.speech_rate)
        rate_layout.addWidget(rate_label)
        rate_layout.addWidget(self.rate_slider)
        speech_group_layout.addLayout(rate_layout)
        
        # Тексты для озвучивания
        text_group_layout = QVBoxLayout()
        text_group_layout.addWidget(QLabel("Тексты для озвучивания"))
        
        # Текст для подключения
        join_layout = QHBoxLayout()
        join_label = QLabel("При подключении:")
        self.join_text_input = QLineEdit(self.viewmodel.settings.join_text)
        join_layout.addWidget(join_label)
        join_layout.addWidget(self.join_text_input)
        text_group_layout.addLayout(join_layout)
        
        # Текст для лайка
        like_layout = QHBoxLayout()
        like_label = QLabel("При лайке:")
        self.like_text_input = QLineEdit(self.viewmodel.settings.like_text)
        like_layout.addWidget(like_label)
        like_layout.addWidget(self.like_text_input)
        text_group_layout.addLayout(like_layout)
        
        # Задержка звуковых уведомлений
        delay_layout = QHBoxLayout()
        delay_label = QLabel("Задержка звуковых уведомлений (мс):")
        self.delay_input = QSpinBox()
        self.delay_input.setMinimum(0)
        self.delay_input.setMaximum(5000)
        self.delay_input.setValue(self.viewmodel.settings.notify_delay)
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.delay_input)
        
        # Кнопка сохранения настроек
        save_btn = QPushButton("Сохранить настройки")
        save_btn.clicked.connect(self.save_settings)
        
        # Добавляем все в основной layout
        layout.addLayout(speech_group_layout)
        layout.addLayout(text_group_layout)
        layout.addLayout(delay_layout)
        layout.addWidget(save_btn)
        layout.addStretch(1)  # Пространство внизу
        
        tab.setLayout(layout)
        return tab
    
    def create_sound_tab(self):
        """Создает вкладку настроек звуков"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Таблица для привязки звуков к ID подарков
        self.sounds_table = QTableWidget()
        self.sounds_table.setColumnCount(3)
        self.sounds_table.setHorizontalHeaderLabels(["ID подарка", "Звук", "Действия"])
        self.sounds_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.sounds_table)
        
        # Добавление новой привязки
        add_layout = QHBoxLayout()
        
        self.gift_id_input = QSpinBox()
        self.gift_id_input.setMinimum(1)
        self.gift_id_input.setMaximum(999999)
        
        self.sound_combo = QComboBox()
        self.update_sound_combo()  # Заполняем список доступных звуков
        
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_sound_mapping)
        
        add_layout.addWidget(QLabel("ID подарка:"))
        add_layout.addWidget(self.gift_id_input)
        add_layout.addWidget(QLabel("Звук:"))
        add_layout.addWidget(self.sound_combo)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        
        # Кнопка обновления списка звуков
        refresh_btn = QPushButton("Обновить список звуков")
        refresh_btn.clicked.connect(self.update_sound_combo)
        layout.addWidget(refresh_btn)
        
        # Заполняем таблицу звуков
        self.update_sounds_table()
        
        tab.setLayout(layout)
        return tab
    
    def bind_data(self):
        """Настраивает привязки данных между UI и ViewModel"""
        # Привязка полей ввода
        self.stream_input.setText(self.viewmodel.stream)
        self.stream_input.textChanged.connect(self.update_stream)
        
        # Привязка чекбоксов
        self.notify_gift_chk.setChecked(self.viewmodel.notify_gift)
        self.speech_gift_chk.setChecked(self.viewmodel.speech_gift)
        self.speech_like_chk.setChecked(self.viewmodel.speech_like)
        self.speech_member_chk.setChecked(self.viewmodel.speech_member)
        
        self.notify_gift_chk.stateChanged.connect(self.update_notify_gift)
        self.speech_gift_chk.stateChanged.connect(self.update_speech_gift)
        self.speech_like_chk.stateChanged.connect(self.update_speech_like)
        self.speech_member_chk.stateChanged.connect(self.update_speech_member)
        
        # Регистрируем колбэки для уведомлений об изменениях во ViewModel
        self.viewmodel.add_callback('is_monitoring', self.update_monitoring_button)
        self.viewmodel.add_callback('item_list', self.update_events_table)
    
    def update_ui(self):
        """Обновляет UI по таймеру"""
        # Обновление таблицы событий происходит по уведомлениям от ViewModel
        pass
    
    def update_stream(self, text):
        """Обновляет ID стрима в ViewModel"""
        self.viewmodel.stream = text
    
    def update_notify_gift(self, state):
        """Обновляет настройку звукового оповещения о донатах"""
        self.viewmodel.notify_gift = (state == Qt.CheckState.Checked)
    
    def update_speech_gift(self, state):
        """Обновляет настройку озвучивания донатов"""
        self.viewmodel.speech_gift = (state == Qt.CheckState.Checked)
    
    def update_speech_like(self, state):
        """Обновляет настройку озвучивания лайков"""
        self.viewmodel.speech_like = (state == Qt.CheckState.Checked)
    
    def update_speech_member(self, state):
        """Обновляет настройку озвучивания подключений"""
        self.viewmodel.speech_member = (state == Qt.CheckState.Checked)
    
    def toggle_monitoring(self):
        """Включает или выключает мониторинг"""
        if not self.viewmodel.stream:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, укажите ID стрима")
            return
        
        self.viewmodel.start_monitoring()
    
    def update_monitoring_button(self):
        """Обновляет текст кнопки мониторинга"""
        if self.viewmodel.is_monitoring:
            self.monitor_btn.setText("Остановить мониторинг")
            self.monitor_btn.setStyleSheet("background-color: #ffaaaa;")
        elif self.viewmodel.is_processing:
            self.monitor_btn.setText("Подключение...")
            self.monitor_btn.setEnabled(False)
        else:
            self.monitor_btn.setText("Начать мониторинг")
            self.monitor_btn.setStyleSheet("")
            self.monitor_btn.setEnabled(True)
    
    def update_events_table(self):
        """Обновляет таблицу событий"""
        self.events_table.setRowCount(len(self.viewmodel.item_list))
        
        for i, item in enumerate(self.viewmodel.item_list):
            # Время
            time_item = QTableWidgetItem(item.timestamp.strftime("%H:%M:%S"))
            self.events_table.setItem(i, 0, time_item)
            
            # Пользователь
            user_item = QTableWidgetItem(item.name)
            self.events_table.setItem(i, 1, user_item)
            
            # Событие
            event_item = QTableWidgetItem(item.event)
            self.events_table.setItem(i, 2, event_item)
            
            # Подсветка важных событий
            if item.alert_level == AlertLevel.IMPORTANT:
                for col in range(3):
                    cell_item = self.events_table.item(i, col)
                    cell_item.setBackground(Qt.GlobalColor.yellow)
    
    def save_settings(self):
        """Сохраняет настройки"""
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
        
        QMessageBox.information(self, "Настройки", "Настройки успешно сохранены")
    
    def update_sound_combo(self):
        """Обновляет список доступных звуков"""
        self.sound_combo.clear()
        sounds = self.viewmodel.sound_service.sound_list()
        if sounds:
            self.sound_combo.addItems(sounds)
    
    def update_sounds_table(self):
        """Обновляет таблицу привязок звуков к ID подарков"""
        # Очищаем таблицу
        self.sounds_table.setRowCount(0)
        
        # Получаем список привязок
        sound_mappings = self.viewmodel.sound_service.play_list()
        
        # Заполняем таблицу
        for i, (gift_id, sound_file) in enumerate(sound_mappings):
            self.sounds_table.insertRow(i)
            
            # ID подарка
            id_item = QTableWidgetItem(str(gift_id))
            self.sounds_table.setItem(i, 0, id_item)
            
            # Название звукового файла
            sound_item = QTableWidgetItem(sound_file)
            self.sounds_table.setItem(i, 1, sound_item)
            
            # Кнопки действий
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            # Кнопка воспроизведения
            play_btn = QPushButton("▶")
            play_btn.setMaximumWidth(30)
            play_btn.clicked.connect(lambda _, s=sound_file: self.play_sound(s))
            
            # Кнопка удаления
            delete_btn = QPushButton("✕")
            delete_btn.setMaximumWidth(30)
            delete_btn.clicked.connect(lambda _, gid=gift_id: self.remove_sound_mapping(gid))
            
            actions_layout.addWidget(play_btn)
            actions_layout.addWidget(delete_btn)
            
            self.sounds_table.setCellWidget(i, 2, actions_widget)
    
    def play_sound(self, sound_file):
        """Воспроизводит выбранный звук"""
        # Используем звуковой сервис для воспроизведения
        # Здесь мы используем временный ID -1, который не будет сохраняться
        self.viewmodel.sound_service.play(-1, 0)  # Задержка 0 мс для немедленного воспроизведения
    
    def add_sound_mapping(self):
        """Добавляет новую привязку звука к ID подарка"""
        gift_id = self.gift_id_input.value()
        sound_file = self.sound_combo.currentText()
        
        if not sound_file:
            QMessageBox.warning(self, "Ошибка", "Звуковой файл не выбран")
            return
        
        # Добавляем привязку
        self.viewmodel.sound_service.update(gift_id, sound_file)
        
        # Обновляем таблицу
        self.update_sounds_table()
    
    def remove_sound_mapping(self, gift_id):
        """Удаляет привязку звука к ID подарка"""
        # В SoundService нет метода для удаления, поэтому обновляем на пустое значение
        self.viewmodel.sound_service.update(gift_id, "")
        
        # Обновляем таблицу
        self.update_sounds_table()