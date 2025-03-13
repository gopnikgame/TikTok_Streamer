import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Импортируем компоненты
from services.speech_service import SpeechService
from services.sound_service import SoundService
from services.gift_service import GiftService
from viewmodels.monitoring_viewmodel import MonitoringViewModel
from views.main_window import MainWindow

def main():
    # Создаем папку для ассетов, если её нет
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    # Создаем приложение
    app = QApplication(sys.argv)
    app.setApplicationName("TTStreamerPy")
    
    # Создаем сервисы
    speech_service = SpeechService()
    sound_service = SoundService()
    gift_service = GiftService()
    
    # Создаем ViewModel
    monitoring_viewmodel = MonitoringViewModel(speech_service, sound_service, gift_service)
    
    # Создаем и показываем главное окно
    main_window = MainWindow(monitoring_viewmodel)
    main_window.show()
    
    # Запускаем цикл обработки событий
    sys.exit(app.exec())

if __name__ == "__main__":
    main()