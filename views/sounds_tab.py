# views/sounds_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QSpinBox, QListView, QAbstractItemView, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6 import sip
from models.data_models import AlertLevel, TableItemView, GiftData
from utils.error_handler import ErrorHandler
from utils.logger import Logger
from PyQt6 import sip
from datetime import datetime
import os
import shutil

class SoundsTab(QWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.error_handler = ErrorHandler()
        self.logger = Logger().get_logger('SoundsTab')
        self.logger.info("������������� ������� ������")
        self.init_ui()
        self.bind_events()
        self.update_sounds_list()
        self.update_mappings_list()
        self.logger.debug("������� ������ ����������������")

    def init_ui(self):
        """�������������� ���������������� ��������� ������� ������"""
        try:
            layout = QVBoxLayout()
            # ������ ��� �������� ������
            upload_layout = QHBoxLayout()
            upload_btn = QPushButton("��������� ����")
            upload_btn.clicked.connect(self.upload_sound)
            upload_layout.addWidget(upload_btn)
            upload_layout.addStretch(1)
            layout.addLayout(upload_layout)
            self.logger.debug("������� ������ ��� �������� ������")
            # ������ ��������� ������
            layout.addWidget(QLabel("��������� �����:"))
            self.sounds_model = QStandardItemModel()
            self.sounds_list = QListView()
            self.sounds_list.setModel(self.sounds_model)
            self.sounds_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            layout.addWidget(self.sounds_list)
            self.logger.debug("������ ������ ��������� ������")
            # �������� ������ � ID ��������
            layout.addWidget(QLabel("�������� ������ � ID ��������:"))
            mapping_layout = QHBoxLayout()
            self.gift_id_input = QSpinBox()
            self.gift_id_input.setRange(1, 999999)
            self.sound_combo = QComboBox()
            self.add_mapping_btn = QPushButton("��������")
            self.add_mapping_btn.clicked.connect(self.add_sound_mapping)
            mapping_layout.addWidget(QLabel("ID �������:"))
            mapping_layout.addWidget(self.gift_id_input)
            mapping_layout.addWidget(QLabel("����:"))
            mapping_layout.addWidget(self.sound_combo, 1)
            mapping_layout.addWidget(self.add_mapping_btn)
            layout.addLayout(mapping_layout)
            self.logger.debug("������� ������ ��� �������� ������ � ID ��������")
            # ������ �������� ������
            layout.addWidget(QLabel("������� ��������:"))
            self.mappings_model = QStandardItemModel()
            self.mappings_list = QListView()
            self.mappings_list.setModel(self.mappings_model)
            self.mappings_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            layout.addWidget(self.mappings_list)
            self.logger.debug("������ ������ �������� ������")
            self.setLayout(layout)
        except Exception as e:
            self.logger.error(f"������ ��� �������� ������� ������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ �������� ����������", 
                                              "�� ������� ������� ������� ������", str(e))

    def bind_events(self):
        """����������� ����������� ������� � ���������� ViewModel"""
        try:
            self.logger.debug("����������� ������� ���������")
        except Exception as e:
            self.logger.error(f"������ ��� �������� ������������ �������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ �������������", 
                                             "�� ������� ��������� ����������� �������", str(e))

    def update_sounds_list(self):
        """��������� ������ ��������� ������"""
        try:
            self.sounds_model.clear()
            self.sound_combo.clear()
            if not os.path.exists("assets"):
                os.makedirs("assets")
                self.logger.info("������� ���������� assets")
            # �������� ������ �������� ������
            sound_files = [f for f in os.listdir("assets") if f.lower().endswith(('.mp3', '.wav'))]
            for sound in sound_files:
                self.sounds_model.appendRow(QStandardItem(sound))
                self.sound_combo.addItem(sound)
            self.logger.debug(f"�������� ������ ������: {len(sound_files)} ������")
        except Exception as e:
            self.logger.error(f"������ ��� ���������� ������ ������: {str(e)}", exc_info=True)
            self.error_handler.handle_file_error(self, e, "assets")

    def update_mappings_list(self):
        """��������� ������ �������� ������ � ID ��������"""
        try:
            self.mappings_model.clear()
            # �������� ������� ��������
            mappings = self.viewmodel.sound_service.get_mappings()
            for gift_id, sound_file in mappings.items():
                self.mappings_model.appendRow(
                    QStandardItem(f"ID {gift_id}: {sound_file}")
                )
            self.logger.debug(f"�������� ������ ��������: {len(mappings)} ��������")
        except Exception as e:
            self.logger.error(f"������ ��� ���������� ������ ��������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ ���������� ������", 
                                                 "�� ������� �������� ������ ��������", str(e))

    def upload_sound(self):
        """��������� ����� �������� ����"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "�������� �������� ����", "", "����� ����� (*.mp3 *.wav)"
            )
            if not file_path:
                return
            # �������� ���� � ���������� assets
            file_name = os.path.basename(file_path)
            destination = os.path.join("assets", file_name)
            try:
                # ���������, ���������� �� ���������� assets
                if not os.path.exists("assets"):
                    os.makedirs("assets")
                # �������� ����
                shutil.copy2(file_path, destination)
                self.logger.info(f"�������� ���� ��������: {file_name}")
                # ��������� ������
                self.update_sounds_list()
                QMessageBox.information(self, "�������� �����", f"���� {file_name} ������� ��������")
            except Exception as e:
                self.logger.error(f"������ ��� ����������� ��������� �����: {str(e)}", exc_info=True)
                self.error_handler.handle_file_error(self, e, destination)
        except Exception as e:
            self.logger.error(f"������ ��� �������� �����: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ �������� �����", 
                                                 "�� ������� ��������� �������� ����", str(e))

    def add_sound_mapping(self):
        """��������� ����� �������� ����� � ID �������"""
        try:
            gift_id = self.gift_id_input.value()
            sound_file = self.sound_combo.currentText()
            if not sound_file:
                self.error_handler.show_validation_error(self, "����������, �������� �������� ����")
                return
            # ��������� ��������
            self.viewmodel.sound_service.add_mapping(gift_id, sound_file)
            self.logger.info(f"��������� �������� �����: ID {gift_id} -> {sound_file}")
            # ��������� ������ ��������
            self.update_mappings_list()
            QMessageBox.information(
                self, 
                "�������� �����", 
                f"������� � ID {gift_id} ������ ����� �������������� ������ {sound_file}"
            )
        except Exception as e:
            self.logger.error(f"������ ��� ���������� �������� �����: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ �������� �����", 
                                                 "�� ������� ��������� ���� � ID �������", str(e))