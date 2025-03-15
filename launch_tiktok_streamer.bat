@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title TikTok Streamer Launcher
:: Установка цветовых схем
color 0A
:: Создаем временную папку для скачивания
if not exist ".\temp" mkdir ".\temp"
echo ===============================================================
echo           TikTok Streamer - Запуск приложения
echo ===============================================================
echo.

:: Проверяем наличие Python
echo [*] Проверка наличия Python...
where python >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo [-] Python не найден. Необходимо установить Python.
    goto install_python
) else (
    echo [+] Python установлен, проверяем версию...
)

:: Проверяем версию Python (нужна 3.8 или выше)
for /f "tokens=2 delims= " %%I in ('python --version 2^>^&1') do set PY_VERSION=%%I
if "!PY_VERSION!"=="" (
    echo [-] Не удалось определить версию Python.
    goto install_python
)
for /f "tokens=1,2 delims=." %%I in ("!PY_VERSION!") do (
    set PY_MAJOR=%%I
    set PY_MINOR=%%J
)
echo [*] Версия Python: !PY_MAJOR!.!PY_MINOR!
if !PY_MAJOR! LSS 3 (
    echo [-] Версия Python слишком старая. Требуется Python 3.8 или выше.
    goto install_python
)
if !PY_MAJOR! EQU 3 (
    if !PY_MINOR! LSS 8 (
        echo [-] Версия Python слишком старая. Требуется Python 3.8 или выше.
        goto install_python
    )
)
echo [+] Версия Python соответствует требованиям.

:: Проверяем наличие папки assets
if not exist "assets" (
    echo [*] Создание папки assets...
    mkdir "assets"
    echo [+] Папка assets создана.
) else (
    echo [+] Папка assets уже существует.
)

:: Проверка и установка зависимостей
echo [*] Проверка и установка зависимостей...
:: Обновляем pip
echo [*] Обновление pip...
python -m pip install --upgrade pip >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo [-] Ошибка при обновлении pip.
    goto check_deps_error
)

:: Проверяем, существует ли файл requirements.txt
if not exist "requirements.txt" (
    echo [-] Файл requirements.txt не найден!
    echo [*] Создаем файл requirements.txt с необходимыми зависимостями...
    (
        echo PyQt6>=6.5.0
        echo pyttsx3>=2.90
        echo pygame>=2.5.0
        echo TikTokLive==6.4.4
        echo aiohttp>=3.8.0
        echo requests>=2.28.0
    ) > requirements.txt
    echo [+] Файл requirements.txt создан.
)

:: Устанавливаем зависимости из requirements.txt
echo [*] Установка зависимостей из requirements.txt...
python -m pip install -r requirements.txt >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo [-] Ошибка при установке зависимостей.
    echo [*] Пробуем установить основные компоненты напрямую...
    for %%m in (PyQt6 pyttsx3 pygame TikTokLive aiohttp requests) do (
        echo [*] Установка %%m...
        python -m pip install %%m >nul 2>&1
        if !ERRORLEVEL! neq 0 (
            echo [-] Ошибка при установке %%m.
            goto check_deps_error
        )
    )
)

:: Проверяем установку каждой зависимости
set DEPS_OK=1
echo [*] Проверка установки зависимостей...
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
    goto check_deps_error
) else (
    echo [+] Все зависимости успешно установлены.
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
    goto run_error
)

echo [+] Приложение успешно запущено.
pause
exit /b 0

:install_python
echo [*] Скачивание и установка Python 3.10...
:: Скачиваем Python
if exist ".\temp\python_installer.exe" (
    del /f /q ".\temp\python_installer.exe"
)
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe' -OutFile '.\temp\python_installer.exe'}"
if !ERRORLEVEL! neq 0 (
    echo [-] Ошибка при скачивании Python. Проверьте подключение к интернету.
    echo [!] Пожалуйста, скачайте и установите Python вручную с https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Устанавливаем Python (тихая установка с добавлением в PATH)
echo [*] Установка Python 3.10...
.\temp\python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_doc=0
if !ERRORLEVEL! neq 0 (
    echo [-] Ошибка при тихой установке Python.
    echo [*] Запускаем установщик в графическом режиме...
    echo [!] ВАЖНО: Отметьте опцию "Add Python to PATH" в установщике!
    start "" ".\temp\python_installer.exe"
    echo [!] После завершения установки перезапустите этот скрипт.
    pause
    exit /b 1
)

:: Обновляем переменную PATH для текущей сессии
set "PATH=%PATH%;%USERPROFILE%\AppData\Local\Programs\Python\Python310\Scripts;%USERPROFILE%\AppData\Local\Programs\Python\Python310"
echo [+] Python 3.10 успешно установлен.
echo [!] Пожалуйста, перезапустите этот скрипт для продолжения.
echo [!] Не забудьте ЗАКРЫТЬ И ОТКРЫТЬ ЗАНОВО командную строку/PowerShell!
pause
exit /b 0

:check_deps_error
echo [!] Ошибка при установке зависимостей.
echo [!] Пожалуйста, установите зависимости вручную:
echo [!] pip install -r requirements.txt
pause
exit /b 1

:run_error
echo [!] Ошибка при запуске приложения.
echo [!] Пожалуйста, проверьте файл error.log, если он существует.
pause
exit /b 1