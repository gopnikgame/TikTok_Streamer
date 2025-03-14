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
    echo [!] Для установки Visual C++ Redistributable рекомендуется запустить от имени администратора
    echo [!] Некоторые функции могут работать некорректно
    echo.
    choice /C YN /M "Продолжить без прав администратора?"
    if !ERRORLEVEL! equ 2 (
        exit /b 1
    )
)

:: Проверяем наличие Visual C++ Redistributable
echo [*] Проверка наличия Microsoft Visual C++ Redistributable...
if not exist "%SystemRoot%\System32\vcruntime140.dll" (
    echo [-] Visual C++ Redistributable не установлен!
    goto install_vcredist
) else (
    echo [+] Visual C++ Redistributable найден, проверяем библиотеки api-ms-win-crt...
)

:: Проверяем наличие файлов api-ms-win-crt*.dll
:: Правильно инициализируем переменную перед использованием
set API_MS_DLL_COUNT=0
for /f %%a in ('dir /b "%SystemRoot%\System32\api-ms-win-crt*.dll" 2^>^&1 ^| find /c /v ""') do (
    set API_MS_DLL_COUNT=%%a
)

:: Вывод количества найденных файлов для диагностики
echo [*] Найдено файлов api-ms-win-crt*.dll: !API_MS_DLL_COUNT!

if !API_MS_DLL_COUNT! LSS 5 (
    echo [-] Недостаточно системных библиотек api-ms-win-crt*.dll: !API_MS_DLL_COUNT!
    goto install_vcredist
) else (
    echo [+] Системные библиотеки api-ms-win-crt*.dll найдены в достаточном количестве.
)

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
goto check_deps

:install_vcredist
echo.
echo [*] Необходима установка Microsoft Visual C++ Redistributable...
echo [*] Скачиваем установщик...

:: Удаляем старый файл, если он существует
if exist ".\temp\vc_redist.x64.exe" (
    del /f /q ".\temp\vc_redist.x64.exe"
)

:: Скачиваем установщик Visual C++ Redistributable через PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile '.\temp\vc_redist.x64.exe'}"
if !ERRORLEVEL! neq 0 (
    echo [-] Ошибка при скачивании установщика Visual C++ Redistributable.
    echo [!] Пожалуйста, скачайте и установите Visual C++ Redistributable вручную:
    echo [!] https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
    echo [!] Вы также можете попробовать скачать напрямую с сервера Microsoft:
    echo [!] https://download.visualstudio.microsoft.com/download/pr/9e94e996-9961-4443-9dce-0f8d862222bd/64AFC5FC94DEF5C830F7333D522A6F631D2C621A6F4E7886272D9D8DE37E6471/VC_redist.x64.exe
    echo.
    echo [!] После установки перезапустите этот скрипт.
    pause
    exit /b 1
)

:: Проверяем, что файл действительно скачался
if not exist ".\temp\vc_redist.x64.exe" (
    echo [-] Файл установщика не был скачан корректно.
    echo [!] Пожалуйста, скачайте и установите Visual C++ Redistributable вручную.
    pause
    exit /b 1
)

echo [*] Запуск установки Visual C++ Redistributable...
echo [*] Это может занять некоторое время, пожалуйста, подождите...
echo [*] Размер файла установщика: 
for %%A in (".\temp\vc_redist.x64.exe") do (
    echo [*] %%~zA байт
)

:: Запускаем установщик с ожиданием завершения
start /wait "Visual C++ Installer" ".\temp\vc_redist.x64.exe" /install /quiet /norestart
if !ERRORLEVEL! neq 0 (
    echo [-] Ошибка при установке Visual C++ Redistributable (код: !ERRORLEVEL!).
    echo [!] Пробуем запустить установку в обычном режиме...
    echo [!] Следуйте инструкциям в установщике и нажимайте "Далее"...
    start "" ".\temp\vc_redist.x64.exe"
    echo [!] После завершения установки перезапустите этот скрипт.
    pause
    exit /b 1
)

echo [+] Microsoft Visual C++ Redistributable успешно установлен.
echo [*] Продолжаем проверку других компонентов...

:: После установки VCRedist проверяем наличие Python
goto check_python

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