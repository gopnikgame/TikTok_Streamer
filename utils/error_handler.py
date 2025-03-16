import traceback
import sys
from PyQt6.QtWidgets import QMessageBox
from utils.logger import Logger

class ErrorHandler:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ErrorHandler, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """
        Инициализация обработчика ошибок
        """
        self.logger = Logger().get_logger('ErrorHandler')
        self.logger.info("Инициализация обработчика ошибок")
        
        # Устанавливаем глобальный обработчик исключений
        sys.excepthook = self.handle_global_exception
    
    def handle_global_exception(self, exc_type, exc_value, exc_traceback):
        """
        Обрабатывает необработанные исключения в приложении
        """
        try:
            error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.logger.critical(f"Необработанное исключение: {error_msg}")
            
            # Выводим сообщение пользователю
            message = (f"Произошла критическая ошибка:\n"
                       f"{exc_type.__name__}: {str(exc_value)}\n\n"
                       f"Детали сохранены в журнале.")
            QMessageBox.critical(None, "Критическая ошибка", message)
            
            # Вызываем оригинальный excepthook чтобы приложение корректно завершилось
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        except Exception as e:
            self.logger.error(f"Ошибка при обработке глобального исключения: {str(e)}", exc_info=True)
    
    def handle_network_error(self, parent_widget, error, operation=None):
        """
        Обрабатывает сетевые ошибки
        """
        try:
            error_str = str(error)
            operation_str = f" при {operation}" if operation else ""
            
            self.logger.error(f"Сетевая ошибка{operation_str}: {error_str}")
            
            message = f"Произошла сетевая ошибка{operation_str}.\n\n{error_str}"
            QMessageBox.warning(parent_widget, "Ошибка сети", message)
            
            # Возвращаем False чтобы вызывающий код мог проверить успешность операции
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при обработке сетевой ошибки: {str(e)}", exc_info=True)
            return False
    
    def handle_tiktok_error(self, parent_widget, error):
        """
        Обрабатывает ошибки API TikTok
        """
        try:
            error_str = str(error)
            self.logger.error(f"Ошибка API TikTok: {error_str}")
            
            # Анализируем ошибку и даём осмысленные рекомендации
            suggestion = ""
            if "connection" in error_str.lower() or "timeout" in error_str.lower():
                suggestion = "\n\nПроверьте подключение к Интернету и повторите попытку."
            elif "not found" in error_str.lower() or "404" in error_str:
                suggestion = "\n\nПроверьте правильность ID стрима. Возможно, пользователь не ведет стрим в данный момент."
            elif "permission" in error_str.lower() or "403" in error_str:
                suggestion = "\n\nДоступ к стриму запрещен. Возможно, это приватный стрим."
            
            message = f"Ошибка при взаимодействии с TikTok API:\n{error_str}{suggestion}"
            QMessageBox.warning(parent_widget, "Ошибка TikTok API", message)
            
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при обработке ошибки TikTok API: {str(e)}", exc_info=True)
            return False
    
    def handle_file_error(self, parent_widget, error, file_path=None):
        """
        Обрабатывает ошибки работы с файлами
        """
        try:
            file_info = f" '{file_path}'" if file_path else ""
            error_str = str(error)
            
            self.logger.error(f"Ошибка файловой операции{file_info}: {error_str}")
            
            # Анализируем ошибку и даём осмысленные рекомендации
            suggestion = ""
            if "permission" in error_str.lower():
                suggestion = "\n\nПроверьте права доступа к файлу и папке."
            elif "no such file" in error_str.lower():
                suggestion = "\n\nУкажите существующий путь к файлу."
            elif "disk full" in error_str.lower() or "no space" in error_str.lower():
                suggestion = "\n\nНедостаточно свободного места на диске."
            
            message = f"Ошибка при работе с файлом{file_info}:\n{error_str}{suggestion}"
            QMessageBox.warning(parent_widget, "Ошибка файловой операции", message)
            
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при обработке ошибки файловой операции: {str(e)}", exc_info=True)
            return False
    
    def show_validation_error(self, parent_widget, message):
        """
        Показывает сообщение об ошибке валидации данных
        """
        try:
            self.logger.warning(f"Ошибка валидации: {message}")
            
            QMessageBox.warning(parent_widget, "Ошибка валидации", message)
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при показе ошибки валидации: {str(e)}", exc_info=True)
            return False
    
    def show_error_dialog(self, parent_widget, title, message, details=None):
        """
        Показывает диалог с ошибкой и дополнительными деталями
        """
        try:
            self.logger.error(f"{title}: {message}")
            
            msg_box = QMessageBox(parent_widget)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            
            if details:
                msg_box.setDetailedText(details)
            
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
        except Exception as e:
            self.logger.error(f"Ошибка при показе диалога ошибки: {str(e)}", exc_info=True)
