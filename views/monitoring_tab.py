# views/monitoring_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QCheckBox, QTableView
from PyQt6.QtCore import Qt
from models.data_models import AlertLevel, TableItemView, GiftData
from utils.error_handler import ErrorHandler
from utils.logger import Logger
from PyQt6 import sip
from datetime import datetime
from .main_window import EventsTableModel

class MonitoringTab(QWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.error_handler = ErrorHandler()
        self.logger = Logger().get_logger('MonitoringTab')
        self.logger.info("������������� ������� �����������")
        self.init_ui()
        self.bind_events()
        self.update_monitoring_state()
        self.logger.debug("������� ����������� ����������������")

    def init_ui(self):
        """�������������� ���������������� ��������� ������� �����������"""
        try:
            layout = QVBoxLayout()
            # ������ � ����� ��� ID ������ � ������� �������
            stream_layout = QHBoxLayout()
            stream_label = QLabel("ID ������:")
            self.stream_input = QLineEdit()
            self.stream_input.setText(self.viewmodel.stream)
            self.toggle_btn = QPushButton("������ ����������")
            stream_layout.addWidget(stream_label)
            stream_layout.addWidget(self.stream_input, 1)
            stream_layout.addWidget(self.toggle_btn)
            layout.addLayout(stream_layout)
            self.logger.debug("������� ������ ��� ID ������ � ������ �������")
            # �������� ��� ��������
            checks_layout = QHBoxLayout()
            self.notify_chk = QCheckBox("�������� ����������")
            self.notify_chk.setChecked(self.viewmodel.notify_gift)
            self.speech_gift_chk = QCheckBox("���������� �������")
            self.speech_gift_chk.setChecked(self.viewmodel.speech_gift)
            self.speech_like_chk = QCheckBox("���������� �����")
            self.speech_like_chk.setChecked(self.viewmodel.speech_like)
            self.speech_member_chk = QCheckBox("���������� �����������")
            self.speech_member_chk.setChecked(self.viewmodel.speech_member)
            checks_layout.addWidget(self.notify_chk)
            checks_layout.addWidget(self.speech_gift_chk)
            checks_layout.addWidget(self.speech_like_chk)
            checks_layout.addWidget(self.speech_member_chk)
            layout.addLayout(checks_layout)
            self.logger.debug("������� �������� ��� ��������")
            # ������� �������
            self.table_model = EventsTableModel(self.viewmodel)
            self.table_view = QTableView()
            self.table_view.setModel(self.table_model)
            self.table_view.horizontalHeader().setStretchLastSection(True)
            layout.addWidget(self.table_view, 1)
            self.logger.debug("������� ������� �������")
            # ������
            self.status_label = QLabel("������: ����� � �����������")
            layout.addWidget(self.status_label)
            self.setLayout(layout)
        except Exception as e:
            self.logger.error(f"������ ��� �������� ������� �����������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ �������� ����������", 
                                              "�� ������� ������� ������� �����������", str(e))

    def bind_events(self):
        """����������� ����������� ������� � ���������� ViewModel"""
        try:
            self.toggle_btn.clicked.connect(self.toggle_monitoring)
            self.notify_chk.clicked.connect(self.toggle_notify_gift)
            self.speech_gift_chk.clicked.connect(self.toggle_speech_gift)
            self.speech_like_chk.clicked.connect(self.toggle_speech_like)
            self.speech_member_chk.clicked.connect(self.toggle_speech_member)
            self.logger.debug("����������� ������� ���������")
        except Exception as e:
            self.logger.error(f"������ ��� �������� ������������ �������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ �������������", 
                                             "�� ������� ��������� ����������� �������", str(e))

    def update_monitoring_state(self):
        """��������� ��������� ���������� � ����������� �� ������� �����������"""
        try:
            if self.viewmodel.is_processing:
                self.toggle_btn.setEnabled(False)
                self.status_label.setText("������: �����������...")
                self.stream_input.setEnabled(False)
                self.logger.debug("��������� ���������: �����������...")
            elif self.viewmodel.is_monitoring:
                self.toggle_btn.setText("���������� ����������")
                self.toggle_btn.setEnabled(True)
                self.status_label.setText(f"������: ���������� ������ {self.viewmodel.stream}")
                self.stream_input.setEnabled(False)
                self.logger.debug(f"��������� ���������: ���������� ������ {self.viewmodel.stream}")
            else:
                self.toggle_btn.setText("������ ����������")
                self.toggle_btn.setEnabled(True)
                self.status_label.setText("������: ����� � �����������")
                self.stream_input.setEnabled(True)
                self.logger.debug("��������� ���������: ����� � �����������")
        except Exception as e:
            self.logger.error(f"������ ��� ���������� ��������� �����������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ ���������� ����������", 
                                             "�� ������� �������� ��������� ����������", str(e))

    def toggle_monitoring(self):
        """�������� ��� ��������� ����������"""
        try:
            if self.viewmodel.is_monitoring:
                self.logger.info("��������� �����������")
                self.viewmodel.stop_monitoring()
                return
            # �������� ID ������ �� ���� �����
            stream = self.stream_input.text().strip()
            if not stream:
                self.logger.warning("������� ������ ���������� ��� �������� ID ������")
                self.error_handler.show_validation_error(self, "����������, ������� ID ������")
                return
            # ��������� ID ������ � ������ � ��������� ����������
            self.logger.info(f"������ ����������� ������: {stream}")
            self.viewmodel.stream = stream
            self.viewmodel.start_monitoring()
        except Exception as e:
            self.logger.error(f"������ ��� ������������ �����������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ �����������", 
                                                 "�� ������� �������� ��������� �����������", str(e))

    def toggle_notify_gift(self):
        """�������� ��� ��������� �������� ���������� � ��������"""
        try:
            self.viewmodel.notify_gift = self.notify_chk.isChecked()
            self.logger.debug(f"��������� �������� ���������� ��������: {self.viewmodel.notify_gift}")
        except Exception as e:
            self.logger.error(f"������ ��� ��������� ��������� �������� ����������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ ��������", 
                                                 "�� ������� �������� ��������� �������� ����������", str(e))

    def toggle_speech_gift(self):
        """�������� ��� ��������� ����������� ��������"""
        try:
            self.viewmodel.speech_gift = self.speech_gift_chk.isChecked()
            self.logger.debug(f"��������� ����������� �������� ��������: {self.viewmodel.speech_gift}")
        except Exception as e:
            self.logger.error(f"������ ��� ��������� ��������� ����������� ��������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ ��������", 
                                                 "�� ������� �������� ��������� ����������� ��������", str(e))

    def toggle_speech_like(self):
        """�������� ��� ��������� ����������� ������"""
        try:
            self.viewmodel.speech_like = self.speech_like_chk.isChecked()
            self.logger.debug(f"��������� ����������� ������ ��������: {self.viewmodel.speech_like}")
        except Exception as e:
            self.logger.error(f"������ ��� ��������� ��������� ����������� ������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ ��������", 
                                                 "�� ������� �������� ��������� ����������� ������", str(e))

    def toggle_speech_member(self):
        """�������� ��� ��������� ����������� �����������"""
        try:
            self.viewmodel.speech_member = self.speech_member_chk.isChecked()
            self.logger.debug(f"��������� ����������� ����������� ��������: {self.viewmodel.speech_member}")
        except Exception as e:
            self.logger.error(f"������ ��� ��������� ��������� ����������� �����������: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(self, "������ ��������", 
                                                 "�� ������� �������� ��������� ����������� �����������", str(e))