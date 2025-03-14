@echo off
setlocal enabledelayedexpansion

echo.
echo ===================================================
echo =       TikTok Streamer - Программа запуска       =
echo ===================================================
echo.

:: Проверяем наличие администраторских прав
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Запуск программы без прав администратора.
    echo [!] Некоторые функции могут не работать корректно.
    echo [!] Рекомендуется перезапустить от имени администратора.
    echo.
    choice /C YN /M "Продолжить без прав администратора?"
    if !errorlevel! equ 2 (
        exit /b 1
    )
)

:: Проверяем наличие Python
echo [*] Проверка установки Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [-] Python не найден в системе!
    goto install_python
) else (
    for /f "tokens=* USEBACKQ" %%F in (`python --version`) do set PYTHON_VERSION=%%F
    echo [+] Найден !PYTHON_VERSION!
)

:: Проверяем версию Python
echo [*] Проверка версии Python...
python -c "import sys; exit(1) if sys.version_info < (3,8) else exit(0)" 2>nul
if %errorlevel% neq 0 (
    echo [-] Установленная версия Python устарела!
    echo [-] Требуется Python 3.8 или выше.
    goto install_python
) else (
    echo [+] Версия Python соответствует требованиям.
)

:: Проверяем наличие Visual C++ Redistributable
echo [*] Проверка наличия Visual C++ Redistributable...
if not exist "%SystemRoot%\System32\vcruntime140.dll" (
    echo [-] Visual C++ Redistributable не установлен!
    goto install_vcredist
) else (
    echo [+] Visual C++ Redistributable установлен.
)

:: Проверяем наличие файлов api-ms-win-crt*.dll
echo [*] Проверка наличия системных библиотек api-ms-win-crt*.dll...
set API_MS_DLL_MISSING=0
for /f "tokens=*" %%a in ('dir /b "%SystemRoot%\System32\api-ms-win-crt*.dll" 2^>nul') do (
    set /a API_MS_DLL_COUNT+=1
)

if !API_MS_DLL_COUNT! LSS 5 (
    echo [-] Отсутствуют системные библиотеки api-ms-win-crt*.dll!
    set API_MS_DLL_MISSING=1
    goto install_vcredist
) else (
    echo [+] Системные библиотеки api-ms-win-crt*.dll найдены.
)

goto check_deps

:install_vcredist
echo.
echo [*] Необходима установка Microsoft Visual C++ Redistributable...
echo [*] Скачиваем установщик...

:: Создаем временную директорию
if not exist "temp" mkdir temp

:: Скачиваем установщик Visual C++ Redistributable
powershell -Command "& {Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile 'temp\vc_redist.x64.exe'}"
if %errorlevel% neq 0 (
    echo [-] Ошибка при скачивании установщика.
    echo [!] Пожалуйста, скачайте и установите Microsoft Visual C++ Redistributable вручную:
    echo [!] https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo [!] После установки перезапустите этот скрипт.
    pause
    exit /b 1
)

echo [*] Запуск установки Visual C++ Redistributable...
temp\vc_redist.x64.exe /install /quiet /norestart
if %errorlevel% neq 0 (
    echo [-] Ошибка при установке Visual C++ Redistributable.
    echo [!] Попробуйте установить вручную:
    echo [!] temp\vc_redist.x64.exe
    pause
    exit /b 1
)

echo [+] Microsoft Visual C++ Redistributable успешно установлен.
goto check_deps

:install_python
echo.
echo [*] Необходима установка Python 3.10...
echo [*] Скачиваем установщик Python...

:: Создаем временную директорию
if not exist "temp" mkdir temp

:: Скачиваем установщик Python 3.10
powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.8/python-3.10.8-amd64.exe' -OutFile 'temp\python_installer.exe'}"
if %errorlevel% neq 0 (
    echo [-] Ошибка при скачивании Python. Проверьте подключение к интернету.
    echo [!] Пожалуйста, скачайте и установите Python вручную с https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [*] Запуск установки Python 3.10...
echo [*] ВАЖНО: Отметьте опцию "Add Python to PATH" в установщике!
start /wait temp\python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
if %errorlevel% neq 0 (
    echo [-] Ошибка при установке Python.
    echo [!] Попробуйте установить Python 3.10 вручную.
    pause
    exit /b 1
)

echo [+] Python 3.10 успешно установлен.
echo [!] Пожалуйста, перезапустите этот скрипт для продолжения.
echo [!] Не забудьте ЗАКРЫТЬ И ОТКРЫТЬ ЗАНОВО командную строку/PowerShell!
pause
exit /b 0

:check_deps
echo.
echo [*] Проверка и установка зависимостей...

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
        echo TikTokLive==6.4.4
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
    
    for %%m in (PyQt6 pyttsx3 pygame TikTokLive aiohttp requests) do (
        python -m pip install %%m
        if !ERRORLEVEL! neq 0 (
            echo [-] Ошибка при установке %%m.
        )
    )
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
    echo [!] Детали ошибки можно найти в логах.
    pause
    exit /b 1
)

exit /b 0