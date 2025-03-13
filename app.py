import sys
import os
import traceback
from typing import Optional

# Импорт обработчика ошибок запуска
try:
    from utils.startup_error_handler import StartupErrorHandler
except ImportError:
    # Если не удается импортировать обработчик, используем базовые функции
    def show_error(title: str, message: str) -> None:
        print(f"{title}: {message}")
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)
        except:
            pass
    
    try:
        with open("startup_error.log", "w") as f:
            f.write(f"Критическая ошибка при импорте обработчика ошибок:\n")
            f.write(traceback.format_exc())
    except:
        pass
        
    show_error("Критическая ошибка", "Не удалось запустить приложение. Проверьте наличие всех файлов программы.")
    sys.exit(1)

def main():
    # Проверка окружения перед импортом остальных модулей
    issues = StartupErrorHandler.check_environment()
    if issues:
        error_message = StartupErrorHandler.format_error_message(issues)
        StartupErrorHandler.show_error_messagebox("Проблемы с зависимостями", error_message)
        sys.exit(1)
    
    # Только после проверки окружения импортируем остальные модули
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon
        
        # Импортируем компоненты
        from services.speech_service import SpeechService
        from services.sound_service import SoundService
        from services.gift_service import GiftService
        from viewmodels.monitoring_viewmodel import MonitoringViewModel
        from views.main_window import MainWindow
        from utils.logger import Logger
        from utils.error_handler import ErrorHandler
        
        # Инициализируем логгер
        logger = Logger().get_logger()
        logger.info("Запуск приложения TTStreamerPy")
        
        # Инициализируем обработчик ошибок
        error_handler = ErrorHandler()
        
        # Создаем папку для ассетов, если её нет
        try:
            if not os.path.exists("assets"):
                os.makedirs("assets")
                logger.info("Создана директория assets")
        except Exception as e:
            error_handler.handle_file_error(None, e, "assets")
        
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
            error_handler.show_error_dialog(None, "Критическая ошибка", 
                                            "Не удалось запустить приложение", 
                                            str(e))
            logger.critical(f"Критическая ошибка при запуске: {str(e)}", exc_info=True)
            sys.exit(1)
    except Exception as e:
        # Обработка исключений на этапе импорта
        StartupErrorHandler.handle_startup_error(e)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Отлов неперехваченных исключений самого верхнего уровня
        StartupErrorHandler.handle_startup_error(e)
        sys.exit(1)