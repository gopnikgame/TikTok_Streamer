import os
import sys
import platform
import importlib.util
import traceback
import ctypes
from typing import List, Dict

class StartupErrorHandler:
    """
    Обработчик ошибок запуска приложения
    """
    
    # Список необходимых библиотек/модулей для проверки
    REQUIRED_MODULES = [
        "PyQt6", 
        "pyttsx3", 
        "pygame", 
        "TikTokLive", 
        "aiohttp", 
        "requests"
    ]
    
    # Список необходимых DLL для Windows (только имена файлов)
    REQUIRED_DLLS_WINDOWS = [
        "vcruntime140.dll",       # Visual C++ Runtime
        "msvcp140.dll",           # Visual C++ Runtime
        "api-ms-win-crt-runtime-l1-1-0.dll",  # Universal C Runtime
        "api-ms-win-crt-stdio-l1-1-0.dll",    # Universal C Runtime
        "api-ms-win-crt-math-l1-1-0.dll"      # Universal C Runtime
    ]
    
    # Сообщения о решениях распространенных проблем
    ERROR_SOLUTIONS = {
        "PyQt6": "Установите PyQt6: pip install PyQt6>=6.5.0",
        "pyttsx3": "Установите pyttsx3: pip install pyttsx3>=2.90",
        "pygame": "Установите pygame: pip install pygame>=2.5.0",
        "TikTokLive": "Установите TikTokLive: pip install TikTokLive==6.4.4",
        "aiohttp": "Установите aiohttp: pip install aiohttp>=3.8.0",
        "requests": "Установите requests: pip install requests>=2.28.0",
        "DLL_ERROR": "Запустите скрипт launch_tiktok_streamer.bat, который автоматически установит Microsoft Visual C++ Redistributable",
        "VCRUNTIME_ERROR": "Запустите скрипт launch_tiktok_streamer.bat, который автоматически установит Microsoft Visual C++ Redistributable",
        "API_MS_WIN_CRT_ERROR": "Запустите скрипт launch_tiktok_streamer.bat, который автоматически установит Microsoft Visual C++ Redistributable"
    }
    
    @staticmethod
    def check_imports() -> List[str]:
        """
        Проверяет наличие всех необходимых импортов
        """
        missing_modules = []
        
        for module_name in StartupErrorHandler.REQUIRED_MODULES:
            if importlib.util.find_spec(module_name) is None:
                missing_modules.append(module_name)
        
        return missing_modules
    
    @staticmethod
    def check_dlls() -> List[str]:
        """
        Проверяет наличие необходимых DLL на Windows
        """
        missing_dlls = []
        
        # Проверяем DLL только на Windows
        if platform.system() != "Windows":
            return missing_dlls
        
        # Проверяем наличие DLL в системных директориях
        system_paths = os.environ["PATH"].split(os.pathsep)
        system_paths.append(os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32"))
        
        for dll in StartupErrorHandler.REQUIRED_DLLS_WINDOWS:
            # Если имя содержит звездочку, проверяем шаблон
            if "*" in dll:
                prefix = dll.split("*")[0]
                found = False
                for path in system_paths:
                    if os.path.exists(path):
                        for file in os.listdir(path):
                            if file.lower().startswith(prefix.lower()) and file.lower().endswith(".dll"):
                                found = True
                                break
                    if found:
                        break
                if not found:
                    missing_dlls.append(dll)
            else:
                # Проверка конкретного DLL
                found = False
                for path in system_paths:
                    if os.path.exists(path):
                        dll_path = os.path.join(path, dll)
                        if os.path.exists(dll_path):
                            found = True
                            break
                if not found:
                    missing_dlls.append(dll)
        
        return missing_dlls
    
    @staticmethod
    def check_assets_folder() -> bool:
        """
        Проверяет наличие папки assets
        """
        return os.path.exists("assets")
    
    @staticmethod
    def show_error_messagebox(title: str, message: str) -> None:
        """
        Отображает окно с ошибкой в зависимости от ОС
        """
        if platform.system() == "Windows":
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)
        else:
            # Для других ОС просто выводим в консоль
            print(f"{title}: {message}")
    
    @staticmethod
    def get_solution_for_error(error_type: str) -> str:
        """
        Возвращает рекомендацию по решению проблемы
        """
        return StartupErrorHandler.ERROR_SOLUTIONS.get(
            error_type, 
            "Проверьте правильность установки всех компонентов программы"
        )
    
    @staticmethod
    def check_environment() -> Dict[str, List[str]]:
        """
        Проверяет окружение на наличие всех необходимых компонентов
        """
        issues = {}
        
        # Проверяем модули
        missing_modules = StartupErrorHandler.check_imports()
        if missing_modules:
            issues["missing_modules"] = missing_modules
        
        # Проверяем DLL на Windows
        if platform.system() == "Windows":
            missing_dlls = StartupErrorHandler.check_dlls()
            if missing_dlls:
                issues["missing_dlls"] = missing_dlls
        
        # Проверяем наличие папки assets
        if not StartupErrorHandler.check_assets_folder():
            issues["missing_folders"] = ["assets"]
        
        return issues
    
    @staticmethod
    def format_error_message(issues: Dict[str, List[str]]) -> str:
        """
        Форматирует сообщение об ошибке на основе обнаруженных проблем
        """
        message = "При запуске программы возникли следующие проблемы:\n\n"
        
        if "missing_modules" in issues:
            message += "Отсутствуют следующие Python модули:\n"
            for module in issues["missing_modules"]:
                message += f"- {module} ({StartupErrorHandler.get_solution_for_error(module)})\n"
            message += "\n"
        
        if "missing_dlls" in issues:
            message += "Отсутствуют следующие системные библиотеки:\n"
            for dll in issues["missing_dlls"]:
                message += f"- {dll}\n"
            message += f"\nРешение: {StartupErrorHandler.get_solution_for_error('DLL_ERROR')}\n\n"
        
        if "missing_folders" in issues:
            message += "Отсутствуют следующие папки:\n"
            for folder in issues["missing_folders"]:
                message += f"- {folder}\n"
            message += "\nСоздайте эти папки в директории с программой или переустановите приложение.\n"
        
        return message
    
    @staticmethod
    def handle_startup_error(e: Exception) -> None:
        """
        Обрабатывает ошибку запуска приложения
        """
        error_message = f"Произошла критическая ошибка при запуске приложения:\n\n{str(e)}\n\n"
        
        # Проверяем типичные ошибки и добавляем решения
        if "ImportError" in str(type(e)) or "ModuleNotFoundError" in str(type(e)):
            module_name = str(e).split("'")[1] if "'" in str(e) else "Unknown"
            error_message += f"Решение: {StartupErrorHandler.get_solution_for_error(module_name)}\n\n"
        elif "DLL" in str(e) or "dll" in str(e):
            error_message += f"Решение: {StartupErrorHandler.get_solution_for_error('DLL_ERROR')}\n\n"
        elif "api-ms-win-crt" in str(e).lower():
            error_message += f"Решение: {StartupErrorHandler.get_solution_for_error('API_MS_WIN_CRT_ERROR')}\n\n"
        
        # Добавляем полный стек-трейс для отладки
        error_message += "Технические детали ошибки (для разработчиков):\n"
        error_message += traceback.format_exc()
        
        # Выводим сообщение
        StartupErrorHandler.show_error_messagebox("Ошибка запуска", error_message)
        
        # Записываем ошибку в файл лога
        try:
            with open("startup_error.log", "w", encoding="utf-8") as f:
                f.write(f"[{platform.system()} {platform.version()}]\n")
                f.write(f"Python {sys.version}\n\n")
                f.write(error_message)
        except Exception as log_error:
            print(f"Ошибка записи лога: {log_error}")