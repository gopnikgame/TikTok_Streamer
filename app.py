import sys
import os
import traceback
import io
from typing import Optional
import logging
import ctypes

# Установка кодировки UTF-8 для стандартного вывода
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Настройка кодировки консоли для Windows
if sys.platform == 'win32':
    k32 = ctypes.windll.kernel32
    k32.SetConsoleOutputCP(65001)  # 65001 - это код UTF-8
    k32.SetConsoleCP(65001)

# Импорт обработчика ошибок запуска
try:
    from utils.startup_error_handler import StartupErrorHandler
except ImportError:
    def show_error(title: str, message: str) -> None:
        print(f"{title}: {message}")
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)
        except:
            pass
    
    try:
        with open("startup_error.log", "w", encoding="utf-8") as f:
            f.write(f"Критическая ошибка при импорте обработчика ошибок:\n")
            f.write(traceback.format_exc())
    except:
        pass
        
    show_error("Критическая ошибка", "Не удалось запустить приложение. Проверьте наличие всех файлов программы.")
    sys.exit(1)

class Logger:
    def __init__(self):
        self.logger = logging.getLogger('TTStreamerPy')
        self.logger.setLevel(logging.DEBUG)
        
        file_handler = logging.FileHandler('app.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger

def main():
    issues = StartupErrorHandler.check_environment()
    if issues:
        error_message = StartupErrorHandler.format_error_message(issues)
        StartupErrorHandler.show_error_messagebox("Проблемы с зависимостями", error_message)
        sys.exit(1)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon
        
        from services.speech_service import SpeechService
        from services.sound_service import SoundService
        from services.gift_service import GiftService
        from viewmodels.monitoring_viewmodel import MonitoringViewModel
        from views.main_window import MainWindow
        from utils.logger import Logger
        from utils.error_handler import ErrorHandler
        
        logger = Logger().get_logger()
        logger.info("Запуск приложения TTStreamerPy")
        
        error_handler = ErrorHandler()
        
        try:
            if not os.path.exists("assets"):
                os.makedirs("assets")
                logger.info("Создана директория assets")
            else:
                logger.debug("Директория assets уже существует")
        except Exception as e:
            error_handler.handle_file_error(None, e, "assets")
            logger.error(f"Ошибка при создании директории assets: {str(e)}", exc_info=True)
        
        try:
            app = QApplication(sys.argv)
            app.setApplicationName("TTStreamerPy")
            logger.debug("Создано приложение QApplication")
        except Exception as e:
            error_handler.show_error_dialog(None, "Критическая ошибка", 
                                            "Не удалось создать приложение", 
                                            str(e))
            logger.critical(f"Критическая ошибка при создании QApplication: {str(e)}", exc_info=True)
            sys.exit(1)
        
        try:
            logger.debug("Инициализация сервисов")
            speech_service = SpeechService()
            sound_service = SoundService()
            gift_service = GiftService()
            
            logger.debug("Инициализация ViewModel")
            monitoring_viewmodel = MonitoringViewModel(speech_service, sound_service, gift_service)
            
            logger.debug("Создание главного окна")
            main_window = MainWindow(monitoring_viewmodel)
            main_window.show()
            logger.info("Приложение запущено")
            
            sys.exit(app.exec())
        except Exception as e:
            error_handler.show_error_dialog(None, "Критическая ошибка", 
                                            "Не удалось запустить приложение", 
                                            str(e))
            logger.critical(f"Критическая ошибка при запуске: {str(e)}", exc_info=True)
            sys.exit(1)
    except Exception as e:
        StartupErrorHandler.handle_startup_error(e)
        logger.critical(f"Критическая ошибка на этапе импорта: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        StartupErrorHandler.handle_startup_error(e)
        logger.critical(f"Критическая ошибка самого верхнего уровня: {str(e)}", exc_info=True)
        sys.exit(1)