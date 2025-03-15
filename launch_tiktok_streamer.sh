#!/bin/bash
# Установка цветов для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функция для вывода с отступом и цветом
print_message() {
    local color=$1
    local prefix=$2
    local message=$3
    echo -e "${color}${prefix} ${message}${NC}"
}

clear
echo -e "${GREEN}==============================================================="
echo -e "           TikTok Streamer - Запуск приложения"
echo -e "===============================================================${NC}"
echo ""

# Создаем временную папку для скачивания
if [ ! -d "./temp" ]; then
    mkdir -p "./temp"
fi

# Проверяем наличие Python
print_message "$CYAN" "[*]" "Проверка наличия Python..."
if ! command -v python3 &> /dev/null; then
    print_message "$RED" "[-]" "Python не найден. Необходимо установить Python."
    # Определяем дистрибутив Linux
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    else
        DISTRO="unknown"
    fi
    print_message "$YELLOW" "[!]" "Определен дистрибутив: $DISTRO"
    # Предлагаем установку в зависимости от дистрибутива
    case $DISTRO in
        ubuntu|debian|linuxmint)
            print_message "$CYAN" "[*]" "Попытка установки Python через apt..."
            read -p "Хотите установить Python 3 прямо сейчас? (y/n): " install_python
            if [ "$install_python" == "y" ] || [ "$install_python" == "Y" ]; then
                sudo apt update
                sudo apt install -y python3 python3-pip python3-venv
                if [ $? -ne 0 ]; then
                    print_message "$RED" "[-]" "Ошибка при установке Python. Установите вручную с помощью команды:"
                    print_message "$YELLOW" "[!]" "sudo apt install python3 python3-pip python3-venv"
                    exit 1
                else
                    print_message "$GREEN" "[+]" "Python успешно установлен."
                fi
            else
                print_message "$YELLOW" "[!]" "Установите Python вручную с помощью команды:"
                print_message "$YELLOW" "[!]" "sudo apt install python3 python3-pip python3-venv"
                exit 1
            fi
            ;;
        fedora|centos|rhel)
            print_message "$CYAN" "[*]" "Попытка установки Python через dnf/yum..."
            read -p "Хотите установить Python 3 прямо сейчас? (y/n): " install_python
            if [ "$install_python" == "y" ] || [ "$install_python" == "Y" ]; then
                if command -v dnf &> /dev/null; then
                    sudo dnf install -y python3 python3-pip
                else
                    sudo yum install -y python3 python3-pip
                fi
                if [ $? -ne 0 ]; then
                    print_message "$RED" "[-]" "Ошибка при установке Python. Установите вручную с помощью команды:"
                    print_message "$YELLOW" "[!]" "sudo dnf install python3 python3-pip" "или" "sudo yum install python3 python3-pip"
                    exit 1
                else
                    print_message "$GREEN" "[+]" "Python успешно установлен."
                fi
            else
                print_message "$YELLOW" "[!]" "Установите Python вручную с помощью команды:"
                print_message "$YELLOW" "[!]" "sudo dnf install python3 python3-pip" "или" "sudo yum install python3 python3-pip"
                exit 1
            fi
            ;;
        arch|manjaro)
            print_message "$CYAN" "[*]" "Попытка установки Python через pacman..."
            read -p "Хотите установить Python 3 прямо сейчас? (y/n): " install_python
            if [ "$install_python" == "y" ] || [ "$install_python" == "Y" ]; then
                sudo pacman -Sy --noconfirm python python-pip
                if [ $? -ne 0 ]; then
                    print_message "$RED" "[-]" "Ошибка при установке Python. Установите вручную с помощью команды:"
                    print_message "$YELLOW" "[!]" "sudo pacman -Sy python python-pip"
                    exit 1
                else
                    print_message "$GREEN" "[+]" "Python успешно установлен."
                fi
            else
                print_message "$YELLOW" "[!]" "Установите Python вручную с помощью команды:"
                print_message "$YELLOW" "[!]" "sudo pacman -Sy python python-pip"
                exit 1
            fi
            ;;
        *)
            print_message "$YELLOW" "[!]" "Неизвестный дистрибутив. Установите Python 3 вручную через ваш пакетный менеджер."
            exit 1
            ;;
    esac
else
    print_message "$GREEN" "[+]" "Python установлен, проверяем версию..."
fi

# Проверяем версию Python (нужна 3.8 или выше)
py_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
py_major=$(echo $py_version | cut -d. -f1)
py_minor=$(echo $py_version | cut -d. -f2)
if [ "$py_major" -lt 3 ] || [ "$py_major" -eq 3 -a "$py_minor" -lt 8 ]; then
    print_message "$RED" "[-]" "Установленная версия Python ($py_version) слишком старая. Требуется Python 3.8 или выше."
    print_message "$YELLOW" "[!]" "Установите более новую версию Python через ваш пакетный менеджер или загрузите с python.org"
    exit 1
else
    print_message "$GREEN" "[+]" "Версия Python ($py_version) соответствует требованиям."
fi

# Проверяем наличие необходимых системных зависимостей для GUI
print_message "$CYAN" "[*]" "Проверка необходимых системных зависимостей для GUI..."

# Функция для установки системных зависимостей в зависимости от дистрибутива
install_system_deps() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    else
        DISTRO="unknown"
    fi
    case $DISTRO in
        ubuntu|debian|linuxmint)
            sudo apt update
            sudo apt install -y python3-pyqt6 libqt6gui6 libqt6widgets6 python3-dev build-essential libespeak-ng1
            ;;
        fedora|centos|rhel)
            if command -v dnf &> /dev/null; then
                sudo dnf install -y python3-PyQt6 qt6-qtbase-gui gcc gcc-c++ python3-devel espeak-ng
            else
                sudo yum install -y python3-PyQt6 qt6-qtbase-gui gcc gcc-c++ python3-devel espeak-ng
            fi
            ;;
        arch|manjaro)
            sudo pacman -Sy --noconfirm python-pyqt6 qt6-base base-devel espeak-ng
            ;;
        *)
            print_message "$YELLOW" "[!]" "Неизвестный дистрибутив. Установите необходимые зависимости для PyQt6 вручную."
            ;;
    esac
}

# Спрашиваем у пользователя, хочет ли он установить системные зависимости
read -p "Установить системные зависимости для графического интерфейса? (y/n): " install_deps
if [ "$install_deps" == "y" ] || [ "$install_deps" == "Y" ]; then
    print_message "$CYAN" "[*]" "Установка системных зависимостей..."
    install_system_deps
    if [ $? -ne 0 ]; then
        print_message "$RED" "[-]" "Ошибка при установке системных зависимостей."
        exit 1
    else
        print_message "$GREEN" "[+]" "Системные зависимости успешно установлены."
    fi
else
    print_message "$YELLOW" "[!]" "Пропуск установки системных зависимостей. Убедитесь, что они установлены."
fi

# Создаем виртуальное окружение, если его нет
print_message "$CYAN" "[*]" "Проверка виртуального окружения..."
if [ ! -d "./venv" ]; then
    print_message "$CYAN" "[*]" "Создание виртуального окружения..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_message "$RED" "[-]" "Ошибка при создании виртуального окружения."
        print_message "$YELLOW" "[!]" "Пробуем установить python3-venv и создать окружение заново..."
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO=$ID
        else
            DISTRO="unknown"
        fi
        case $DISTRO in
            ubuntu|debian|linuxmint)
                sudo apt install -y python3-venv
                ;;
            fedora|centos|rhel)
                if command -v dnf &> /dev/null; then
                    sudo dnf install -y python3-venv
                else
                    sudo yum install -y python3-venv
                fi
                ;;
            arch|manjaro)
                # python-venv уже включен в пакет python в Arch
                ;;
        esac
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            print_message "$RED" "[-]" "Не удалось создать виртуальное окружение. Пробуем без него."
            USE_VENV=0
        else 
            USE_VENV=1
        fi
    else
        USE_VENV=1
    fi
else
    print_message "$GREEN" "[+]" "Виртуальное окружение уже существует."
    USE_VENV=1
fi

# Активация виртуального окружения
if [ $USE_VENV -eq 1 ]; then
    print_message "$CYAN" "[*]" "Активация виртуального окружения..."
    source venv/bin/activate
fi

# Обновление pip
print_message "$CYAN" "[*]" "Обновление pip..."
pip install --upgrade pip

# Проверяем, существует ли файл requirements.txt
if [ ! -f "requirements.txt" ]; then
    print_message "$RED" "[-]" "Файл requirements.txt не найден!"
    print_message "$CYAN" "[*]" "Создаем файл requirements.txt с необходимыми зависимостями..."
    cat > requirements.txt << EOF
PyQt6>=6.8.1
pyttsx3>=2.98
pygame>=2.6.1
TikTokLive==6.4.4
aiohttp>=3.11.13
requests>=2.32.3
EOF
    print_message "$GREEN" "[+]" "Файл requirements.txt создан."
fi

# Устанавливаем зависимости из requirements.txt
print_message "$CYAN" "[*]" "Установка зависимостей из requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_message "$RED" "[-]" "Ошибка при установке зависимостей."
    print_message "$CYAN" "[*]" "Пробуем установить основные компоненты напрямую..."
    for module in PyQt6 pyttsx3 pygame TikTokLive aiohttp requests; do
        pip install "$module"
        if [ $? -ne 0 ]; then
            print_message "$RED" "[-]" "Ошибка при установке $module."
            exit 1
        fi
    done
fi

# Проверка установки зависимостей
print_message "$CYAN" "[*]" "Проверка установки зависимостей..."
DEPS_OK=1
for module in PyQt6 pyttsx3 pygame TikTokLive aiohttp requests; do
    if ! python3 -c "import $module" &> /dev/null; then
        print_message "$RED" "[-]" "Модуль $module не установлен!"
        DEPS_OK=0
    fi
done
if [ $DEPS_OK -eq 0 ]; then
    print_message "$RED" "[-]" "Не все зависимости установлены правильно!"
    print_message "$YELLOW" "[!]" "Попробуйте запустить скрипт от имени администратора или установите их вручную:"
    print_message "$YELLOW" "[!]" "pip install -r requirements.txt"
    exit 1
else
    print_message "$GREEN" "[+]" "Все зависимости успешно установлены."
fi

# Проверяем наличие папки assets
if [ ! -d "assets" ]; then
    print_message "$CYAN" "[*]" "Создание папки assets..."
    mkdir -p "assets"
    print_message "$GREEN" "[+]" "Папка assets создана."
else
    print_message "$GREEN" "[+]" "Папка assets уже существует."
fi

# Проверка прав на запуск файла app.py
if [ ! -x "app.py" ] && [ -f "app.py" ]; then
    print_message "$CYAN" "[*]" "Добавление прав на выполнение для app.py..."
    chmod +x app.py
    print_message "$GREEN" "[+]" "Права на выполнение для app.py добавлены."
else
    print_message "$GREEN" "[+]" "Файл app.py уже имеет права на выполнение."
fi

# Запускаем приложение
print_message "$CYAN" "[*]" "Запуск приложения TikTok Streamer..."
echo ""
python3 app.py
if [ $? -ne 0 ]; then
    echo ""
    print_message "$RED" "[-]" "Произошла ошибка при запуске приложения."
    print_message "$YELLOW" "[!]" "Проверьте файл error.log, если он существует."
    exit 1
else
    print_message "$GREEN" "[+]" "Приложение успешно запущено."
fi

# Если используется виртуальное окружение, деактивируем его
if [ $USE_VENV -eq 1 ]; then
    print_message "$CYAN" "[*]" "Деактивация виртуального окружения..."
    deactivate
fi

read -p "Нажмите Enter для выхода."