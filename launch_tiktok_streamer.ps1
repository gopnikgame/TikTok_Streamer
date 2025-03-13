# Установка кодировки для вывода в консоль
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "TikTok Streamer Launcher"

# Запуск от имени администратора (если требуется)
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Рекомендуется запустить от имени администратора для корректной установки Python и зависимостей" -ForegroundColor Yellow
    $continue = Read-Host "Продолжить без прав администратора? (y/n)"
    if ($continue -ne "y") {
        exit
    }
}

Write-Host "===============================================================" -ForegroundColor Green
Write-Host "           TikTok Streamer - Запуск приложения" -ForegroundColor Green
Write-Host "===============================================================" -ForegroundColor Green
Write-Host

# Создаем временную папку для скачивания
if (-not (Test-Path ".\temp")) {
    New-Item -ItemType Directory -Path ".\temp" | Out-Null
}

# Проверяем наличие Python
Write-Host "[*] Проверка наличия Python..." -ForegroundColor Cyan
$pythonInstalled = $false
try {
    $pythonVersion = (python --version 2>&1) | Out-String
    if ($pythonVersion -match "Python (\d+\.\d+\.\d+)") {
        $pythonInstalled = $true
        $versionMatch = $matches[1] -split "\."
        $majorVersion = [int]$versionMatch[0]
        $minorVersion = [int]$versionMatch[1]
        
        if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 8)) {
            Write-Host "[-] Установленная версия Python слишком старая. Требуется Python 3.8 или выше." -ForegroundColor Red
            $installPython = $true
        } else {
            Write-Host "[+] Версия Python соответствует требованиям: $pythonVersion" -ForegroundColor Green
            $installPython = $false
        }
    }
} catch {
    Write-Host "[-] Python не найден. Необходимо установить Python." -ForegroundColor Red
    $installPython = $true
}

# Устанавливаем Python, если необходимо
if ($installPython) {
    Write-Host "[*] Скачивание и установка Python 3.10..." -ForegroundColor Cyan
    $pythonUrl = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
    $pythonInstaller = ".\temp\python_installer.exe"
    
    try {
        # Скачиваем Python
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
        
        # Устанавливаем Python
        Write-Host "[*] Установка Python 3.10..." -ForegroundColor Cyan
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_test=0", "Include_doc=0" -Wait
        
        # Обновляем переменную PATH для текущей сессии
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine") 
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Process")
        
        Write-Host "[+] Python 3.10 успешно установлен." -ForegroundColor Green
        Write-Host "[*] Продолжаем установку..." -ForegroundColor Cyan
    } catch {
        Write-Host "[-] Ошибка при скачивании или установке Python:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-Host "[!] Посетите сайт: https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "[!] И установите Python 3.10 или новее вручную." -ForegroundColor Yellow
        Read-Host "Нажмите Enter для выхода"
        exit
    }
}

# Проверка и установка зависимостей
Write-Host
Write-Host "[*] Проверка и установка зависимостей..." -ForegroundColor Cyan

# Обновляем pip
Write-Host "[*] Обновление pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip | Out-Null

# Проверяем, существует ли файл requirements.txt
if (-not (Test-Path "requirements.txt")) {
    Write-Host "[-] Файл requirements.txt не найден!" -ForegroundColor Red
    Write-Host "[*] Создаем файл requirements.txt с необходимыми зависимостями..." -ForegroundColor Cyan
    
    @"
PyQt6>=6.5.0
pyttsx3>=2.90
pygame>=2.5.0
TikTokLive>=5.0.0
aiohttp>=3.8.0
requests>=2.28.0
python-logging-loki>=0.3.1
"@ | Out-File -FilePath "requirements.txt" -Encoding utf8NoBOM
    
    Write-Host "[+] Файл requirements.txt создан." -ForegroundColor Green
}

# Устанавливаем зависимости из requirements.txt
Write-Host "[*] Установка зависимостей из requirements.txt..." -ForegroundColor Cyan
$pipResult = $false
try {
    $pipResult = python -m pip install -r requirements.txt 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        $pipResult = $true
    }
} catch {
    $pipResult = $false
}

if (-not $pipResult) {
    Write-Host "[-] Ошибка при установке зависимостей." -ForegroundColor Red
    Write-Host "[*] Пробуем установить основные компоненты напрямую..." -ForegroundColor Cyan
    
    $modules = @("PyQt6", "pyttsx3", "pygame", "TikTokLive", "aiohttp", "requests")
    foreach ($module in $modules) {
        try {
            python -m pip install $module
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[-] Ошибка при установке $module." -ForegroundColor Red
            }
        } catch {
            Write-Host "[-] Ошибка при установке $module:" -ForegroundColor Red
            Write-Host $_.Exception.Message -ForegroundColor Red
        }
    }
}

# Проверяем установку зависимостей
Write-Host
Write-Host "[*] Проверка установки зависимостей..." -ForegroundColor Cyan
$depsOk = $true

$modules = @("PyQt6", "pyttsx3", "pygame", "TikTokLive", "aiohttp", "requests")
foreach ($module in $modules) {
    try {
        $null = python -c "import $module"
    } catch {
        Write-Host "[-] Модуль $module не установлен!" -ForegroundColor Red
        $depsOk = $false
    }
}

if (-not $depsOk) {
    Write-Host "[-] Не все зависимости установлены правильно!" -ForegroundColor Red
    Write-Host "[!] Попробуйте запустить скрипт от имени администратора или установите их вручную:" -ForegroundColor Yellow
    Write-Host "[!] pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Нажмите Enter для выхода"
    exit
} else {
    Write-Host "[+] Все зависимости успешно установлены." -ForegroundColor Green
}

# Проверяем наличие папки assets
if (-not (Test-Path "assets")) {
    Write-Host "[*] Создание папки assets..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path "assets" | Out-Null
}

# Запускаем приложение
Write-Host
Write-Host "[*] Запуск приложения TikTok Streamer..." -ForegroundColor Cyan
Write-Host

try {
    python app.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host
        Write-Host "[-] Произошла ошибка при запуске приложения." -ForegroundColor Red
        Write-Host "[!] Проверьте файл error.log, если он существует." -ForegroundColor Yellow
    }
} catch {
    Write-Host "[-] Произошла ошибка при запуске приложения:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Read-Host "Нажмите Enter для выхода"