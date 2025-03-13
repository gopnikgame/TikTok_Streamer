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
from utils.logger import Logger

def main():
    # Инициализируем логгер
    logger = Logger().get_logger()
    logger.info("Запуск приложения TTStreamerPy")
    
    # Создаем папку для ассетов, если её нет
    if not os.path.exists("assets"):
        os.makedirs("assets")
        logger.info("Создана директория assets")
    
    # Создаем приложение
    app = QApplication(sys.argv)
    app.setApplicationName("TTStreamerPy")
    
    try:
        # Создаем сервисы
        logger.debug("Инициализация сервисов")
        speech_service = SpeechService()
        sound_service = SoundService()
        gift_service = GiftService()
        
        # Создаем ViewModel
        logger.debug("Инициализация ViewModel")
        monitoring_viewmodel = MonitoringViewModel(speech_service, sound_service, gift_service)
        
        # Создаем и показываем главное окно
        logger.debug("Создание главного окна")
        main_window = MainWindow(monitoring_viewmodel)
        main_window.show()
        logger.info("Приложение запущено")
        
        # Запускаем цикл обработки событий
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()