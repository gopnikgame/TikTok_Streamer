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
                self.logger.error(f"Ошибка при загрузке звуковых привязок: {str(e)}", exc_info=True)
        else:
            self.logger.debug(f"Файл {self.store_name} не найден, инициализация пустого словаря")
    
    def sound_list(self):
        """Возвращает список доступных звуковых файлов"""
        try:
            if not os.path.exists("assets"):
                os.makedirs("assets")
                self.logger.info("Создана директория assets")
            
            sounds = [f for f in os.listdir("assets") 
                      if f.lower().endswith(('.wav', '.mp3'))]
            self.logger.debug(f"Найдено {len(sounds)} звуковых файлов: {sounds}")
            return sounds
        except Exception as e:
            self.logger.error(f"Ошибка при получении списка звуковых файлов: {str(e)}", exc_info=True)
            return []
    
    def play_list(self):
        """Возвращает список привязок звуков к ID подарков"""
        try:
            result = [(int(k), v) for k, v in self.store.items()]
            self.logger.debug(f"Список привязок звуков: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Ошибка при получении списка привязок звуков: {str(e)}", exc_info=True)
            return []
    
    def update(self, key, value):
        """Обновляет привязку звука к ID подарка"""
        try:
            key_str = str(key)
            if key_str not in self.store or self.store[key_str] != value:
                self.store[key_str] = value
                try:
                    with open(self.store_name, 'w') as f:
                        json.dump(self.store, f, indent=2)
                    self.logger.debug(f"Обновлена привязка звука для ID {key}: {value}")
                except Exception as e:
                    self.logger.error(f"Ошибка при сохранении звуковых привязок: {str(e)}", exc_info=True)
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении привязки звука: {str(e)}", exc_info=True)
    
    def any(self):
        """Возвращает случайный доступный звуковой файл"""
        try:
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
        except Exception as e:
            self.logger.error(f"Ошибка при выборе случайного звука: {str(e)}", exc_info=True)
            return None
    
    def play(self, key, delay):
        """Запускает воспроизведение звука для ID подарка с задержкой"""
        try:
            self.logger.debug(f"Запрос на воспроизведение звука для ID {key} с задержкой {delay} мс")
            # Выполняем в отдельном потоке, чтобы не блокировать UI
            thread = threading.Thread(target=self._play_thread, args=(key, delay))
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.logger.error(f"Ошибка при запуске воспроизведения звука: {str(e)}", exc_info=True)
    
    def _play_thread(self, key, delay):
        """Воспроизводит звук в отдельном потоке"""
        try:
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
                            self.logger.error(f"Ошибка воспроизведения звука: {str(e)}", exc_info=True)
                    else:
                        self.logger.error(f"Файл не найден: {sound_path}")
                else:
                    self.logger.warning("Нет доступных звуков для воспроизведения")
        except Exception as e:
            self.logger.error(f"Ошибка в потоке воспроизведения звука: {str(e)}", exc_info=True)
    
    def get_mappings(self):
        """Возвращает текущие привязки звуков к ID подарков"""
        try:
            self.logger.debug(f"Получены привязки звуков: {self.store}")
            return self.store
        except Exception as e:
            self.logger.error(f"Ошибка при получении привязок звуков: {str(e)}", exc_info=True)
            return {}