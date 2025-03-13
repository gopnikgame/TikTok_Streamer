import pygame
import json
import os
import random
import time
import threading
from utils.logger import Logger

class SoundService:
    def __init__(self):
        self.logger = Logger().get_logger('SoundService')
        self.logger.info("Инициализация звукового сервиса")
        
        pygame.mixer.init()
        self.logger.debug("Pygame mixer инициализирован")
        
        self.store_name = "giftsounds.json"
        self.store = {}
        self.play_time = 0
        self.lock = threading.Lock()
        
        if os.path.exists(self.store_name):
            try:
                with open(self.store_name, 'r') as f:
                    self.store = json.load(f)
                self.logger.debug(f"Загружено {len(self.store)} звуковых привязок из {self.store_name}")
            except Exception as e:
                self.logger.error(f"Ошибка при загрузке звуковых привязок: {str(e)}")
    
    def sound_list(self):
        if not os.path.exists("assets"):
            os.makedirs("assets")
            self.logger.info("Создана директория assets")
            return []
        
        sounds = [f for f in os.listdir("assets") 
                  if f.lower().endswith(('.wav', '.mp3'))]
        self.logger.debug(f"Найдено {len(sounds)} звуковых файлов")
        return sounds
    
    def play_list(self):
        result = [(int(k), v) for k, v in self.store.items()]
        return result
    
    def update(self, key, value):
        key_str = str(key)
        if key_str not in self.store or self.store[key_str] != value:
            self.store[key_str] = value
            try:
                with open(self.store_name, 'w') as f:
                    json.dump(self.store, f)
                self.logger.debug(f"Обновлена привязка звука для ID {key}: {value}")
            except Exception as e:
                self.logger.error(f"Ошибка при сохранении звуковых привязок: {str(e)}")
    
    def any(self):
        audio_list = self.sound_list()
        for sound in self.store.values():
            if sound in audio_list:
                audio_list.remove(sound)
        
        if not audio_list:
            self.logger.warning("Не найдено свободных звуковых файлов")
            return None
            
        sound = random.choice(audio_list)
        self.logger.debug(f"Выбран случайный звук: {sound}")
        return sound
    
    def play(self, key, delay):
        self.logger.debug(f"Запрос на воспроизведение звука для ID {key} с задержкой {delay} мс")
        # Выполняем в отдельном потоке, чтобы не блокировать UI
        thread = threading.Thread(target=self._play_thread, args=(key, delay))
        thread.daemon = True
        thread.start()
    
    def _play_thread(self, key, delay):
        with self.lock:
            key_str = str(key)
            sound = self.store.get(key_str)
            
            if not sound:
                self.logger.debug(f"Звук для ID {key} не найден, выбираем случайный")
                sound = self.any()
                if sound:
                    self.update(key, sound)
            
            elapsed = time.time() - self.play_time
            wait_time = delay / 1000 - elapsed
            if wait_time > 0:
                self.logger.debug(f"Ожидание {wait_time:.2f} с перед воспроизведением")
                time.sleep(wait_time)
            
            self.play_time = time.time()
            
            if sound:
                sound_path = os.path.join(os.getcwd(), "assets", sound)
                if os.path.exists(sound_path):
                    try:
                        sound_obj = pygame.mixer.Sound(sound_path)
                        sound_obj.play()
                        self.logger.debug(f"Воспроизведение звука: {sound}")
                    except Exception as e:
                        self.logger.error(f"Ошибка воспроизведения звука: {str(e)}")
                else:
                    self.logger.error(f"Файл не найден: {sound_path}")
            else:
                self.logger.warning("Нет доступных звуков для воспроизведения")