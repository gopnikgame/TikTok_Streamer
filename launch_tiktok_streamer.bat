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

:: Проверяем права администратора
echo [*] Проверка прав администратора...
net session >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo [!] Внимание: Скрипт запущен без прав администратора
    echo [!] Для установки системных компонентов рекомендуется запустить от имени администратора
    echo [!] Некоторые функции могут работать некорректно
    echo.
    choice /C YN /M "Продолжить без прав администратора?"
    if !ERRORLEVEL! equ 2 (
        exit /b 1
    )
)

:: Проверяем Windows версию для определения метода установки UCRT
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo [*] Обнаружена Windows версии !VERSION!

:: Определяем нужные компоненты на основе версии Windows
set NEED_UCRT_UPDATE=0
if "!VERSION!"=="6.1" set NEED_UCRT_UPDATE=1
if "!VERSION!"=="6.2" set NEED_UCRT_UPDATE=1
if "!VERSION!"=="6.3" set NEED_UCRT_UPDATE=1

:: Проверяем наличие Visual C++ Redistributable
echo [*] Проверка наличия Microsoft Visual C++ Redistributable...
if not exist "%SystemRoot%\System32\vcruntime140.dll" (
    echo [-] Visual C++ Redistributable не установлен!
    set NEED_VCREDIST=1
) else (
    echo [+] Visual C++ Redistributable найден
    set NEED_VCREDIST=0
)

:: Проверяем наличие файлов Universal C Runtime (api-ms-win-crt*.dll)
echo [*] Проверка наличия Universal C Runtime (UCRT)...
set API_MS_DLL_COUNT=0
for /f %%a in ('dir /b "%SystemRoot%\System32\api-ms-win-crt*.dll" 2^>^&1 ^| find /c /v ""') do (
    set API_MS_DLL_COUNT=%%a
)

:: Вывод количества найденных файлов для диагностики
echo [*] Найдено файлов api-ms-win-crt*.dll: !API_MS_DLL_COUNT!

if !API_MS_DLL_COUNT! LSS 5 (
    echo [-] Недостаточно файлов Universal C Runtime: найдено !API_MS_DLL_COUNT! (требуется минимум 5)
    set NEED_UCRT=1
) else (
    echo [+] Universal C Runtime в порядке.
    set NEED_UCRT=0
)

:: Устанавливаем необходимые компоненты
if !NEED_VCREDIST! EQU 1 goto install_vcredist
if !NEED_UCRT! EQU 1 goto install_ucrt

:: Если все компоненты установлены, переходим к проверке Python
goto check_python

:install_vcredist
echo.
echo [*] Необходима установка Microsoft Visual C++ Redistributable...
echo [*] Скачиваем установщик...

:: Удаляем старый файл, если он существует
if exist ".\temp\vc_redist.x64.exe" (
    del /f /q ".\temp\vc_redist.x64.exe"
)

:: Скачиваем последний Visual C++ Redistributable
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile '.\temp\vc_redist.x64.exe'}"
if !ERRORLEVEL! neq 0 (
    echo [-] Ошибка при скачивании Visual C++ Redistributable.
    echo [!] Пожалуйста, скачайте и установите вручную:
    echo [!] https://aka.ms/vs/17/release/vc_redist.x64.exe
    pause
    exit /b 1
)

echo [*] Запуск установки Visual C++ Redistributable...
echo [*] Это может занять некоторое время, пожалуйста, подождите...

:: Запускаем установщик с ожиданием завершения
start /wait "Visual C++ Installer" ".\temp\vc_redist.x64.exe" /install /quiet /norestart
if !ERRORLEVEL! neq 0 (
    echo [-] Ошибка при установке Visual C++ Redistributable.
    echo [!] Пробуем запустить установку в обычном режиме...
    start "" ".\temp\vc_redist.x64.exe"
    echo [!] После завершения установки перезапустите скрипт.
    pause
    exit /b 1
)

echo [+] Microsoft Visual C++ Redistributable успешно установлен.
if !NEED_UCRT! EQU 1 goto install_ucrt
goto check_python

:install_ucrt
echo.
echo [*] Необходима установка Universal C Runtime (UCRT)...

:: Выбираем метод установки UCRT в зависимости от версии Windows
if !NEED_UCRT_UPDATE! EQU 1 (
    echo [*] Для вашей версии Windows требуется специальное обновление KB2999226
    goto install_ucrt_kb2999226
) else (
    echo [*] Для вашей версии Windows Universal C Runtime устанавливается через компоненты Windows
    goto install_ucrt_windows_features
)

:install_ucrt_kb2999226
echo.
echo [*] Скачиваем обновление KB2999226 (Universal C Runtime)...
echo [*] Определяем разрядность операционной системы...

:: Проверяем, 32-bit или 64-bit система
if exist "%ProgramFiles(x86)%" (
    echo [*] Обнаружена 64-битная система
    set UCRT_URL=https://download.microsoft.com/download/9/6/F/96FD0525-3DDF-423D-8845-5F92F4A6883E/Windows10.0-KB2999226-x64.msu
) else (
    echo [*] Обнаружена 32-битная система
    set UCRT_URL=https://download.microsoft.com/download/1/1/5/11565A9A-EA09-4F0A-A57E-520D5D138140/Windows8.1-KB2999226-x86.msu
)

:: Скачиваем обновление KB2999226
echo [*] Скачиваем обновление Universal C Runtime (UCRT)...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '!UCRT_URL!' -OutFile '.\temp\ucrt_update.msu'}"
if !ERRORLEVEL! neq 0 (
    echo [-] Ошибка при скачивании обновления Universal C Runtime.
    echo [!] Пожалуйста, посетите страницу поддержки Microsoft:
    echo [!] https://support.microsoft.com/ru-ru/help/2999226/update-for-universal-c-runtime-in-windows
    echo [!] Скачайте и установите обновление KB2999226 вручную.
    pause
    exit /b 1
)

:: Устанавливаем обновление
echo [*] Устанавливаем обновление Universal C Runtime...
start /wait wusa.exe .\temp\ucrt_update.msu /quiet /norestart
if !ERRORLEVEL! neq 0 (
    echo [-] Ошибка при установке обновления Universal C Runtime.
    echo [!] Пожалуйста, попробуйте установить вручную:
    echo [!] .\temp\ucrt_update.msu
    pause
    exit /b 1
)

echo [+] Обновление Universal C Runtime успешно установлено.
echo [!] Для завершения установки необходима перезагрузка компьютера.
echo.
choice /C YN /M "Перезагрузить компьютер сейчас?"
if !ERRORLEVEL! equ 1 (
    shutdown.exe /r /t 5 /c "Перезагрузка для завершения установки обновлений"
    echo [*] Компьютер будет перезагружен через 5 секунд...
    echo [!] Запустите скрипт снова после перезагрузки.
    timeout /t 5 > nul
    exit /b 0
) else (
    echo [!] Пожалуйста, перезагрузите компьютер позже для завершения установки.
    echo [!] Затем запустите скрипт снова.
    pause
    exit /b 1
)

:install_ucrt_windows_features
echo [*] Установка компонентов Universal C Runtime через Windows Update...
echo [*] Это может занять некоторое время...

:: Для Windows 10/11 предлагаем обновление через Windows Update
echo [*] Запуск Windows Update для загрузки необходимых компонентов...
start ms-settings:windowsupdate
echo.
echo [!] Откройте Windows Update и установите все доступные обновления.
echo [!] После установки обновлений перезагрузите компьютер и запустите этот скрипт снова.
echo.
echo [!] Также вы можете вручную скачать и установить:
echo [!] 1. Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
echo [!] 2. Universal C Runtime обновление: https://support.microsoft.com/ru-ru/help/2999226
echo.
pause
exit /b 1

:check_python
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
goto check_deps

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
    echo [!] Проверьте файл error.log, если он существует.
)

pause
exit /b 0