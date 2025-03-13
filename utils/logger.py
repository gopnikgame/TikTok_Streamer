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
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        # Настраиваем форматирование логов
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        
        # Настраиваем логирование в файл с ротацией
        file_handler = RotatingFileHandler(
            "logs/app.log", 
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
        self.logger = logging.getLogger('TTStreamerPy')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Предотвращаем дублирование логов
        self.logger.propagate = False
    
    def get_logger(self, name=None):
        """Получает логгер с заданным именем (для компонентов приложения)"""
        if name:
            return logging.getLogger(f'TTStreamerPy.{name}')
        return self.logger