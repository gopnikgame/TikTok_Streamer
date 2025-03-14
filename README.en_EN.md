# TikTok Streamer

[![Russian](https://img.shields.io/badge/Language-Russian-red.svg)](README.md)

## 📋 Table of Contents

- [Description](#-description)
- [Features](#-features)
- [Technologies](#-technologies)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration Options](#-configuration-options)
- [Project Structure](#-project-structure)
- [Support Development](#-support-development)
- [License](#-license)

## ⚠️ Warning

**PROJECT IS UNDER ACTIVE DEVELOPMENT!**

Functionality is not guaranteed. Errors, crashes, and changes in application behavior may occur.
Use at your own risk.

## 📝 Description

TikTok Streamer is a GUI application for monitoring TikTok live streams. It allows tracking activity in TikTok streams, such as user connections, likes, gifts, and responding to these events using sound notifications and text-to-speech synthesis.

## 🚀 Features

- **Stream activity monitoring** — tracking gifts, likes, and user connections
- **Text-to-speech** — announcing events with customizable voice and speech rate
- **Sound notifications** — binding sounds to specific gift IDs
- **Event logging** — maintaining a log of all events with timestamps
- **User-friendly interface** — easy control through a clear graphical interface built with PyQt6
- **Message personalization** — customization of text for likes and connections announcements

## 🖥️ Technologies

- **Python 3.8+** — main development language
- **TikTokLive** — library for connecting to TikTok Live API
- **PyQt6** — graphical user interface
- **pyttsx3** — text-to-speech synthesis
- **pygame** — sound playback
- **aiohttp** — asynchronous HTTP requests for data loading

## 💻 Installation

### Requirements

- Python 3.8+
- Pip (Python package manager)

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/gopnikgame/TikTok_Streamer.git
cd TikTok_Streamer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Launch the application:
   - On Windows: use the `launch_tiktok_streamer.bat` script
   - On Linux/MacOS: use the `launch_tiktok_streamer.sh` script

## 🎮 Usage

1. Launch the application using the appropriate launch script.

2. In the "Monitoring" tab, enter the TikTok stream ID that you want to track.
   - The stream ID is usually the username of the streamer you want to monitor.

3. Click "Start monitoring" to connect to the stream.

4. Configure monitoring parameters using checkboxes:
   - Sound notification
   - Announce gifts
   - Announce likes
   - Announce connections

5. All events will be displayed in real-time at the bottom of the window with timestamps.

## ⚙️ Configuration Options

### "Settings" Tab

- **Voice** — selection of speech synthesizer
- **Speech rate** — adjustment of voice speed
- **Text for connection** — message template when a user connects (@name is replaced with the username)
- **Text for like** — message template for likes (@name is replaced with the username)
- **Delay between sound notifications** — interval in milliseconds

### "Sounds" Tab

- **Sound file upload** — adding MP3 or WAV files for notifications
- **Binding sounds to gift IDs** — setting up specific sound playback for certain gifts

## 📂 Project Structure

```
TikTok_Streamer/
├── app.py              # Application entry point
├── requirements.txt    # Project dependencies
├── assets/             # Folder for sounds and images
├── services/           # Service classes
│   ├── speech_service.py  # Text-to-speech service
│   ├── sound_service.py   # Sound notification service
│   └── gift_service.py    # Gift handling service
├── models/             # Data models
│   └── data_models.py     # Class definitions
├── viewmodels/         # Link between GUI and services
│   └── monitoring_viewmodel.py  # Monitoring ViewModel
├── views/              # View classes (GUI)
│   └── main_window.py     # Main application window
└── utils/              # Utility tools
    ├── error_handler.py   # Error handling
    ├── logger.py          # Logging system
    └── settings.py        # Settings management
```

## 💰 Support Development

If you like this project and want to support its development, you can do so in the following ways:

### 💎 Cryptocurrency
**TON Space**: `UQBh0Cgy5um8oChpXBl8O0NbTwyj1tVXH6RO07c9b3rCD4kf`

### 💳 Fiat Payments
**CloudTips**: [https://pay.cloudtips.ru/p/244b03de](https://pay.cloudtips.ru/p/244b03de)

## 📜 License

This project is distributed under the [MIT](LICENSE) license.

---

© 2025 gopnikgame. All rights reserved.