import os
import logging
from logging.handlers import RotatingFileHandler
import sys

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
        
        # Настраиваем логирование в файл с ротацией
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "app.log"), 
            maxBytes=10*1024*1024,  # 10 МБ
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Настраиваем вывод в консоль
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Создаем и настраиваем корневой логгер
        root_logger = logging.getLogger('TTStreamerPy')
        root_logger.setLevel(logging.DEBUG)
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