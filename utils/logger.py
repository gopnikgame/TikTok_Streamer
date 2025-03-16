import os
import logging
from logging.handlers import RotatingFileHandler
import sys
import locale
import aiofiles
import asyncio
from utils.settings import Settings

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(cls._instance._initialize_logger())
            else:
                asyncio.run(cls._instance._initialize_logger())
        return cls._instance
    
    async def _initialize_logger(self):
        # Логирование информации о системе и кодировках
        await self._log_system_info()
        
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
        
        # Получаем уровень логирования из настроек
        settings = await self._get_settings()
        logging_level = getattr(logging, settings.logging_level.upper(), logging.DEBUG)
        file_handler.setLevel(logging_level)
        
        # Создаем и настраиваем корневой логгер
        root_logger = logging.getLogger('TTStreamerPy')
        root_logger.setLevel(logging_level)
        
        # Удаляем все существующие обработчики перед добавлением новых
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        root_logger.addHandler(file_handler)
        
        # Настраиваем вывод в консоль с учетом поддержки Unicode
        try:
            # Принудительно устанавливаем UTF-8 для всех платформ
            os.environ["PYTHONIOENCODING"] = "utf-8"
            
            # Для Windows дополнительно настраиваем консоль
            if sys.platform == 'win32':
                # Для Python 3.7+ используем reconfigure
                try:
                    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
                except AttributeError:
                    # Для старых версий Python используем ctypes
                    import ctypes
                    k32 = ctypes.windll.kernel32
                    k32.SetConsoleOutputCP(65001)  # 65001 - это код UTF-8
                    k32.SetConsoleCP(65001)
                
            # Создаем консольный обработчик с явным указанием stdout
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
            
            # Логируем успешную настройку консоли
            root_logger.debug("Консольный обработчик логов настроен успешно")
            
        except Exception as e:
            # В случае ошибки при настройке консоли, логируем это в файл
            async with aiofiles.open(os.path.join(log_dir, "console_error.log"), "w", encoding="utf-8") as f:
                await f.write(f"Ошибка при настройке консольного логирования: {str(e)}")
        
        # Предотвращаем дублирование логов
        root_logger.propagate = False
        
        # Сохраняем ссылку на корневой логгер
        self.root_logger = root_logger
        
        # Логируем завершение инициализации
        root_logger.info("Логгер инициализирован успешно")

    async def _get_settings(self):
        """
        Получает настройки с ожиданием их инициализации
        """
        settings = Settings()
        while not hasattr(settings, 'logging_level'):
            await asyncio.sleep(0.1)
        return settings
    
    async def _log_system_info(self):
        """
        Логирует информацию о системе и кодировках для диагностики
        """
        try:
            info = [
                f"Python версия: {sys.version}",
                f"Платформа: {sys.platform}",
                f"Кодировка файловой системы: {sys.getfilesystemencoding()}",
                f"Кодировка стандартного вывода: {sys.stdout.encoding}",
                f"Предпочтительная кодировка: {locale.getpreferredencoding()}",
                f"Текущая локаль: {locale.getlocale()}",
                f"Переменная окружения PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'не установлена')}"
            ]
            
            # Создаем директорию для логов, если её нет
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            # Записываем информацию в отдельный файл
            async with aiofiles.open(os.path.join(log_dir, "system_info.log"), "w", encoding="utf-8") as f:
                await f.write("\n".join(info))
                
        except Exception as e:
            # В случае ошибки, пишем в стандартный диагностический файл
            try:
                async with aiofiles.open("logger_init_error.log", "w", encoding="utf-8") as f:
                    await f.write(f"Ошибка при логировании системной информации: {str(e)}")
            except:
                pass
    
    def get_logger(self, name=None):
        """
        Получает логгер с заданным именем (для компонентов приложения)
        """
        if name:
            child_logger = self.root_logger.getChild(name)
            # Проверяем кодировку и для дочерних логгеров
            child_logger.debug(f"Дочерний логгер '{name}' создан. Проверка кодировки: тест кириллицы")
            return child_logger
        
        # Тестовое сообщение для проверки кодировки
        self.root_logger.debug("Проверка логгера: тест кириллицы")
        return self.root_logger
