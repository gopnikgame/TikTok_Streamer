import os
import logging
from logging.handlers import RotatingFileHandler
import sys
import locale

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        # Создаем директорию для логов, если её нет
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Настраиваем форматирование логов
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        
        # Настраиваем логирование в файл с ротацией с явным указанием UTF-8
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "app.log"), 
            maxBytes=10*1024*1024,  # 10 МБ
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Исправляем вывод в консоль для поддержки Unicode
        # Проверяем текущую кодировку консоли
        try:
            # Для Windows установим кодировку консоли в UTF-8
            if sys.platform == 'win32':
                # Для Python 3.7+ можно использовать следующий способ:
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                console_handler = logging.StreamHandler(sys.stdout)
            else:
                # Для других платформ просто используем стандартный обработчик
                console_handler = logging.StreamHandler(sys.stdout)
        except AttributeError:
            # Для более старых версий Python, где метод reconfigure недоступен
            console_handler = logging.StreamHandler(sys.stdout)
            # Установим обработку ошибок кодирования на 'replace'
            console_handler.setFormatter(logging.Formatter(log_format, None, 'replace'))
        
        console_handler.setLevel(logging.INFO)
        if not hasattr(console_handler, 'formatter'):
            console_handler.setFormatter(formatter)
        
        # Создаем и настраиваем корневой логгер
        root_logger = logging.getLogger('TTStreamerPy')
        root_logger.setLevel(logging.DEBUG)
        
        # Удаляем все существующие обработчики перед добавлением новых
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Предотвращаем дублирование логов
        root_logger.propagate = False
        
        # Сохраняем ссылку на корневой логгер
        self.root_logger = root_logger
    
    def get_logger(self, name=None):
        """Получает логгер с заданным именем (для компонентов приложения)"""
        if name:
            return self.root_logger.getChild(name)
        return self.root_logger