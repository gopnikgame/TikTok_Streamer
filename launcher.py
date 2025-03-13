#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform
import webbrowser

def print_colored(message, color="default"):
    """Выводит цветной текст в консоль, работает и в Windows, и в Linux."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
        "default": "\033[0m",
    }
    
    # Включаем цветной вывод в Windows
    if platform.system() == "Windows":
        os.system("")  # Активирует ANSI-цвета в Windows
    
    print(f"{colors.get(color, colors['default'])}{message}{colors['default']}")

def run_command(command):
    """Запускает команду и возвращает результат выполнения."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python_version():
    """Проверяет версию Python"""
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print_colored(f"Установлена версия Python {version.major}.{version.minor}, но требуется 3.8 или выше.", "red")
            return False
        else:
            print_colored(f"Обнаружена подходящая версия Python: {version.major}.{version.minor}.{version.micro}", "green")
            return True
    except Exception as e:
        print_colored(f"Ошибка при проверке версии Python: {e}", "red")
        return False

def install_dependencies():
    """Устанавливает зависимости из requirements.txt"""
    print_colored("Установка зависимостей...", "cyan")
    
    # Создаем requirements.txt, если его нет
    if not os.path.exists("requirements.txt"):
        print_colored("Файл requirements.txt не найден. Создаем...", "yellow")
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write(
                "PyQt6>=6.5.0\n"
                "pyttsx3>=2.90\n"
                "pygame>=2.5.0\n"
                "TikTokLive>=5.0.0\n"
                "aiohttp>=3.8.0\n"
                "requests>=2.28.0\n"
                "python-logging-loki>=0.3.1\n"
            )
    
    # Обновляем pip
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    
    # Устанавливаем зависимости
    success, output = run_command(f"{sys.executable} -m pip install -r requirements.txt")
    
    if not success:
        print_colored("Ошибка при установке зависимостей из requirements.txt.", "red")
        print_colored("Пробуем установить основные пакеты напрямую...", "yellow")
        
        # Устанавливаем каждый пакет отдельно
        packages = ["PyQt6>=6.5.0", "pyttsx3>=2.90", "pygame>=2.5.0", 
                   "TikTokLive>=5.0.0", "aiohttp>=3.8.0", "requests>=2.28.0"]
        
        for package in packages:
            print_colored(f"Установка {package}...", "cyan")
            run_command(f"{sys.executable} -m pip install {package}")
    
    # Проверяем установку модулей
    all_installed = True
    modules = ["PyQt6", "pyttsx3", "pygame", "TikTokLive", "aiohttp", "requests"]
    
    for module in modules:
        try:
            __import__(module)
        except ImportError:
            print_colored(f"Модуль {module} не установлен!", "red")
            all_installed = False
    
    if all_installed:
        print_colored("Все зависимости успешно установлены.", "green")
        return True
    else:
        print_colored("Не все зависимости установлены корректно.", "red")
        return False

def main():
    """Главная функция запуска приложения."""
    print_colored("===============================================================", "green")
    print_colored("           TikTok Streamer - Запуск приложения", "green")
    print_colored("===============================================================", "green")
    print()
    
    # Создаем папку temp, если её нет
    if not os.path.exists("temp"):
        os.makedirs("temp")
    
    # Проверяем версию Python
    if not check_python_version():