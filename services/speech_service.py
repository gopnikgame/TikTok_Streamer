# services/speech_service.py
import pyttsx3
import threading
from utils.logger import Logger

class SpeechService:
    def __init__(self):
        self.logger = Logger().get_logger('SpeechService')
        self.logger.info("Инициализация сервиса синтеза речи")
        
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)  # Скорость речи по умолчанию
        self.lock = threading.Lock()
        
        self.voices_cache = self.get_voices()
        self.logger.debug(f"Доступные голоса: {', '.join(self.voices_cache)}")
    
    def get_voices(self):
        """Возвращает список доступных голосов"""
        try:
            voices = self.engine.getProperty('voices')
            voice_names = [voice.name for voice in voices]
            self.logger.debug(f"Получен список голосов: {voice_names}")
            return voice_names
        except Exception as e:
            self.logger.error(f"Ошибка при получении списка голосов: {str(e)}", exc_info=True)
            return []

    def set_volume(self, volume):
        """Устанавливает громкость речи"""
        try:
            if 0.0 <= volume <= 1.0:
                self.logger.debug(f"Установлена громкость: {volume}")
                self.engine.setProperty('volume', volume)
            else:
                self.logger.warning("Громкость должна быть в диапазоне от 0.0 до 1.0")
        except Exception as e:
            self.logger.error(f"Ошибка при установке громкости: {str(e)}", exc_info=True)

    def stop(self):
        """Останавливает текущий синтез речи"""
        try:
            self.logger.debug("Остановка синтеза речи")
            self.engine.stop()
        except Exception as e:
            self.logger.error(f"Ошибка при остановке синтеза речи: {str(e)}", exc_info=True)
    
    def speech(self, text, voice_name=None, rate=None, volume=None):
        """Запускает синтез речи в отдельном потоке"""
        try:
            self.logger.debug(f"Запрос на синтез речи: '{text}', голос: {voice_name}, скорость: {rate}, громкость: {volume}")
            # Выполняем в отдельном потоке, чтобы не блокировать UI
            thread = threading.Thread(target=self._speech_thread, args=(text, voice_name, rate, volume))
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.logger.error(f"Ошибка при запуске синтеза речи: {str(e)}", exc_info=True)
    
    def _speech_thread(self, text, voice_name, rate, volume):
        """Синтезирует речь в отдельном потоке"""
        with self.lock:  # Предотвращаем одновременное использование движка
            try:
                if voice_name:
                    voices = self.engine.getProperty('voices')
                    voice_found = False
                    for voice in voices:
                        if voice.name == voice_name:
                            self.logger.debug(f"Установлен голос: {voice_name}")
                            self.engine.setProperty('voice', voice.id)
                            voice_found = True
                            break
                    
                    if not voice_found:
                        self.logger.warning(f"Голос {voice_name} не найден, используется голос по умолчанию")
                
                if rate is not None:
                    real_rate = 150 + (rate * 10)  # Преобразуем из -10..10 в 50..250
                    self.logger.debug(f"Установлена скорость речи: {real_rate}")
                    self.engine.setProperty('rate', real_rate)
                
                if volume is not None:
                    self.set_volume(volume)
                
                self.engine.say(text)
                self.logger.debug(f"Добавлен текст для синтеза: '{text}'")
                self.engine.runAndWait()
                self.logger.debug("Синтез речи выполнен успешно")
            except Exception as e:
                self.logger.error(f"Ошибка при синтезе речи: {str(e)}", exc_info=True)