# views/settings_tab.py
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
        self.logger.info("������������� ������� ��������")
        self.init_ui()
        self.bind_events()
        self.logger.debug("������� �������� ����������������")

    def init_ui(self):
        """�������������� ���������������� ��������� ������� ��������"""
        try:
            layout = QVBoxLayout()
            # �����
            voice_layout = QHBoxLayout()
            voice_layout.addWidget(QLabel("�����:"))
            self.voice_combo = QComboBox()
            try:
                # �������� ������ ��������� �������
                voices = self.viewmodel.speech_service.get_voices()
                self.voice_combo.addItem("") # ������ ������� ��� �������� �� ���������
                self.voice_combo.addItems(voices)
                # ������������� ������� �����, ���� �� �����
                current_voice = self.viewmodel.settings.speech_voice
                if current_voice and current_voice in voices:
                    self.voice_combo.setCurrentText(current_voice)
            except Exception as e:
                self.logger.error(f"������ ��������� ������ �������: {str(e)}", exc_info=True)
                self.error_handler.handle_file_error(self, e, "voices")
            voice_layout.addWidget(self.voice_combo, 1)
            layout.addLayout(voice_layout)
            self.logger.debug("������� ������ ��� ������ ������")
            # �������� ����
            rate_layout = QHBoxLayout()
            rate_layout.addWidget(QLabel("�������� ����:"))
            self.rate_slider = QSlider(Qt.Orientation.Horizontal)
            self.rate_slider.setRange(-10, 10)
            self.rate_slider.setValue(self.viewmodel.settings.speech_rate)
            rate_layout.addWidget(self.rate_slider, 1)
            layout.addLayout(rate_layout)
            self.logger.debug("������� ������ ��� �������� ����")
            # ��������� ����
            volume_layout = QHBoxLayout()
            volume_layout.addWidget(QLabel("��������� ����:"))
            self.volume_slider = QSlider(Qt.Orientation.Horizontal)
            self.volume_slider.setRange(0, 100)  # �������� 0-100 ��� �������� ������������
            self.volume_slider.setValue(int(self.viewmodel.settings.speech_volume * 100))  # ����������� �� 0.0-1.0 � 0-100
            volume_layout.addWidget(self.volume_slider, 1)
            layout.addLayout(volume_layout)
            self.logger.debug("������� ������ ��� ��������� ����")
            # ����� ��� �����������
            join_layout = QHBoxLayout()
            join_layout.addWidget(QLabel("����� ��� �����������:"))
            self.join_text_input = QLineEdit()
            self.join_text_input.setText(self.viewmodel.settings.join_text)
            join_layout.addWidget(self.join_text_input, 1)
            layout.addLayout(join_layout)
            self.logger.debug("������� ������ ��� ������ �����������")
            # ����� ��� �����
            like_layout = QHBoxLayout()
            like_layout.addWidget(QLabel("����� ��� �����:"))
            self.like_text_input = QLineEdit()
            self.like_text_input.setText(self.viewmodel.settings.like_text)
            like_layout.addWidget(self.like_text_input, 1)
            layout.addLayout(like_layout)
            self.logger.debug("������� ������ ��� ������ �����")
            # �������� �������� �����������
            delay_layout = QHBoxLayout()
            delay_layout.addWidget(QLabel("�������� ����� ��������� ������������� (��):"))
            self.delay_input = QSpinBox()
            self.delay_input.setRange(0, 10000)
            self.delay_input.setSingleStep(100)
            self.delay_input.setValue(self.viewmodel.settings.notify_delay)
            delay_layout.addWidget(self.delay_input, 1)
            layout.addLayout(delay_layout)
            self.logger.debug("������� ������ ��� �������� �������� �����������")
            # ������� �����������
            log_level_layout = QHBoxLayout()
            log_level_layout.addWidget(QLabel("������� �����������:"))
            self.log_level_combo = QComboBox()
            self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
            self.log_level_combo.setCurrentText(self.viewmodel.settings.logging_level)
            log_level_layout.addWidget(self.log_level_combo, 1)
            layout.addLayout(log_level_layout)
            self.logger.debug("������� ������ ��� ������ �����������")
            # ���������� TikTok ID
            user_id_layout = QHBoxLayout()
            user_id_layout.addWidget(QLabel("ID ������:"))
            self.user_id_combo = QComboBox()
            self.user_id_combo.addItems(self.viewmodel.settings.saved_user_ids)
            self.user_id_combo.setEditable(True)
            self.user_id_combo.setCurrentText(self.viewmodel.stream)
            user_id_layout.addWidget(self.user_id_combo, 1)
            layout.addLayout(user_id_layout)
            self.logger.debug("������� ������ ��� ������/����� ID ������")
            # ������ ����������
            save_btn = QPushButton("��������� ���������")
            save_btn.clicked.connect(self.save_settings)
            layout.addWidget(save_btn)
            layout.addStretch(1)
            self.setLayout(layout)
        except Exception as e:
            self.logger.error(f"������ ��� �������� ������� ��������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ �������� ����������", 
                                              "�� ������� ������� ������� ��������", str(e))

    def bind_events(self):
        """����������� ����������� ������� � ���������� ViewModel"""
        try:
            self.log_level_combo.currentIndexChanged.connect(self.update_logging_level)
            self.user_id_combo.currentIndexChanged.connect(self.update_user_id)
            self.rate_slider.valueChanged.connect(self.update_speech_rate)
            self.volume_slider.valueChanged.connect(self.update_speech_volume)
            self.logger.debug("����������� ������� ���������")
        except Exception as e:
            self.logger.error(f"������ ��� �������� ������������ �������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ �������������", 
                                             "�� ������� ��������� ����������� �������", str(e))

    def update_logging_level(self, index):
        """��������� ������� �����������"""
        try:
            new_level = self.log_level_combo.currentText()
            self.viewmodel.settings.logging_level = new_level
            self.logger.setLevel(new_level)
            self.logger.debug(f"������� ����������� �������: {new_level}")
        except Exception as e:
            self.logger.error(f"������ ��� ��������� ������ �����������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ ��������", 
                                                "�� ������� �������� ������� �����������", str(e))

    def update_user_id(self, index):
        """��������� ��������� TikTok ID"""
        try:
            new_user_id = self.user_id_combo.currentText()
            if new_user_id not in self.viewmodel.settings.saved_user_ids:
                self.viewmodel.settings.saved_user_ids.append(new_user_id)
                asyncio.run(self.viewmodel.settings.save())  # ��������� ����� ID ������
            self.viewmodel.stream = new_user_id
            self.logger.debug(f"TikTok ID �������: {new_user_id}")
        except Exception as e:
            self.logger.error(f"������ ��� ��������� TikTok ID: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ ��������", 
                                                "�� ������� �������� TikTok ID", str(e))

    def update_speech_rate(self, value):
        """��������� �������� ����"""
        try:
            self.viewmodel.settings.speech_rate = value
            self.logger.debug(f"�������� ���� ��������: {value}")
        except Exception as e:
            self.logger.error(f"������ ��� ��������� �������� ����: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ ��������", 
                                                 "�� ������� �������� �������� ����", str(e))

    def update_speech_volume(self, value):
        """��������� ��������� ����"""
        try:
            volume = value / 100.0  # ����������� �� 0-100 � 0.0-1.0
            self.viewmodel.settings.speech_volume = volume
            self.viewmodel.speech_service.set_volume(volume)
            self.logger.debug(f"��������� ���� ��������: {volume}")
        except Exception as e:
            self.logger.error(f"������ ��� ��������� ��������� ����: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ ��������", 
                                                 "�� ������� �������� ��������� ����", str(e))

    def save_settings(self):
        """��������� ���������"""
        try:
            # ��������� ������
            if self.join_text_input.text().strip() == "":
                self.error_handler.show_validation_error(self, "����� ��� ����������� �� ����� ���� ������")
                return
            if self.like_text_input.text().strip() == "":
                self.error_handler.show_validation_error(self, "����� ��� ����� �� ����� ���� ������")
                return
            # �����
            selected_voice = self.voice_combo.currentText()
            if selected_voice:
                self.viewmodel.settings.speech_voice = selected_voice
            # �������� ����
            self.viewmodel.settings.speech_rate = self.rate_slider.value()
            # ��������� ����
            self.viewmodel.settings.speech_volume = self.volume_slider.value() / 100.0
            # ������
            self.viewmodel.settings.join_text = self.join_text_input.text()
            self.viewmodel.settings.like_text = self.like_text_input.text()
            # �������� �������� �����������
            self.viewmodel.settings.notify_delay = self.delay_input.value()
            # ��������� ���������
            asyncio.run(self.viewmodel.settings.save())
            self.logger.info("��������� ������� ���������")
            QMessageBox.information(self, "���������", "��������� ������� ���������")
        except Exception as e:
            self.logger.error(f"������ ��� ���������� ��������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ ���������� ��������", 
                                                 "�� ������� ��������� ���������", str(e))