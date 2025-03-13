@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title TikTok Streamer Launcher

:: Скрипт запуска TikTok Streamer
:: Показывает прогресс установки и запуска программы

echo ===============================================================
echo           TikTok Streamer - Запуск приложения
echo ===============================================================
echo.

:: Создаем временную папку для скачивания если её нет
if not exist ".\temp" mkdir ".\temp"

:: Проверяем наличие Python
echo [*] Проверка наличия Python...
where python >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo [-] Python не найден. Установка Python...
    goto install_python
) else (
    python -c "import sys; print(sys.version_info[0], '.', sys.version_info[1], sep='')" > .\temp\pyversion.txt
    set /p PYVER=<.\temp\pyversion.txt
    echo [+] Найден Python !PYVER!
    
    :: Проверяем версию Python (нужна 3.8 или выше)
    python -c "import sys; v=sys.version_info; print(1 if (v[0] >= 3 and v[1] >= 8) else 0)" > .\temp\pycheck.txt
    set /p PYCHECK=<.\temp\pycheck.txt
    
    if !PYCHECK! EQU 0 (
        echo [-] Версия Python слишком старая. Требуется 3.8 или выше.
        goto install_python
    ) else (
        echo [+] Версия Python соответствует требованиям.
    )
)
goto install_deps

:install_python
echo [*] Скачивание Python 3.10...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe' -OutFile '.\temp\python_installer.exe'}"
if !ERRORLEVEL! neq 0 (
    echo [-] Ошибка при скачивании Python. Проверьте подключение к интернету.
    echo [!] Посетите сайт: https://www.python.org/downloads/
    echo [!] И установите Python 3.10 или новее вручную.
    pause
    exit /b 1
)

:: Устанавливаем Python (тихая установка с добавлением в PATH)
echo [*] Установка Python 3.10...
.\temp\python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_doc=0
if !ERRORLEVEL! neq 0 (
    echo [-] Ошибка при установке Python. Попробуйте запустить от имени администратора.
    pause
    exit /b 1
)

echo [+] Python 3.10 успешно установлен.
echo [!] Пожалуйста, перезапустите этот скрипт для продолжения.
pause
exit /b 0

:install_deps
echo.
echo [*] Проверка и установка зависимостей...

:: Обновляем переменные окружения, чтобы подхватить новый Python
set PATH=%PATH%;%USERPROFILE%\AppData\Local\Programs\Python\Python310\Scripts\;%USERPROFILE%\AppData\Local\Programs\Python\Python310\

:: Обновляем pip
echo [*] Обновление pip...
python -m pip install --upgrade pip >nul

:: Проверяем, существует ли файл requirements.txt
if not exist "requirements.txt" (
    echo [-] Файл requirements.txt не найден!
    echo [*] Создаем файл requirements.txt с необходимыми зависимостями...
    
    (
        echo PyQt6>=6.5.0
        echo pyttsx3>=2.90
        echo pygame>=2.5.0
        echo TikTokLive>=5.0.0
        echo aiohttp>=3.8.0
        echo requests>=2.28.0
        echo python-logging-loki>=0.3.1
    ) > requirements.txt
    
    echo [+] Файл requirements.txt создан.
)

:: Устанавливаем зависимости из requirements.txt
echo [*] Установка зависимостей из requirements.txt...
python -m pip install -r requirements.txt
if !ERRORLEVEL! neq 0 (
    echo [-] Ошибка при установке зависимостей.
    echo [*] Пробуем установить основные компоненты напрямую...
    
    python -m pip install PyQt6>=6.5.0
    python -m pip install pyttsx3>=2.90
    python -m pip install pygame>=2.5.0
    python -m pip install TikTokLive>=5.0.0
    python -m pip install aiohttp>=3.8.0
    python -m pip install requests>=2.28.0
)

echo.
echo [*] Проверка установки зависимостей...
set DEPS_OK=1

:: Проверяем установку каждой зависимости
for %%m in (PyQt6 pyttsx3 pygame TikTokLive aiohttp requests) do (
    python -c "import %%m" >nul 2>&1 || (
        echo [-] Модуль %%m не установлен!
        set DEPS_OK=0
    )
)

if !DEPS_OK! EQU 0 (
    echo [-] Не все зависимости установлены правильно!
    echo [!] Попробуйте запустить скрипт от имени администратора или установите их вручную:
    echo [!] pip install -r requirements.txt
    pause
    exit /b 1
) else (
    echo [+] Все зависимости успешно установлены.
)

:: Проверяем наличие папки assets
if not exist "assets" (
    echo [*] Создание папки assets...
    mkdir "assets"
)

:: Запускаем приложение
echo.
echo [*] Запуск приложения TikTok Streamer...
echo.
python app.py
if !ERRORLEVEL! neq 0 (
    echo.
    echo [-] Произошла ошибка при запуске приложения.
    echo [!] Проверьте файл error.log, если он существует.
)

pause
exit /b 0