import pygame
import json
import os
import random
import time
import threading

class SoundService:
    def __init__(self):
        pygame.mixer.init()
        self.store_name = "giftsounds.json"
        self.store = {}
        self.play_time = 0
        self.lock = threading.Lock()
        
        if os.path.exists(self.store_name):
            with open(self.store_name, 'r') as f:
                self.store = json.load(f)
    
    def sound_list(self):
        if not os.path.exists("assets"):
            os.makedirs("assets")
            return []
        return [f for f in os.listdir("assets") 
                if f.lower().endswith(('.wav', '.mp3'))]
    
    def play_list(self):
        return [(int(k), v) for k, v in self.store.items()]
    
    def update(self, key, value):
        key_str = str(key)
        if key_str not in self.store or self.store[key_str] != value:
            self.store[key_str] = value
            with open(self.store_name, 'w') as f:
                json.dump(self.store, f)
    
    def any(self):
        audio_list = self.sound_list()
        for sound in self.store.values():
            if sound in audio_list:
                audio_list.remove(sound)
        
        if not audio_list:
            return None
        return random.choice(audio_list)
    
    def play(self, key, delay):
        # Выполняем в отдельном потоке, чтобы не блокировать UI
        thread = threading.Thread(target=self._play_thread, args=(key, delay))
        thread.daemon = True
        thread.start()
    
    def _play_thread(self, key, delay):
        with self.lock:
            key_str = str(key)
            sound = self.store.get(key_str)
            
            if not sound:
                sound = self.any()
                if sound:
                    self.update(key, sound)
            
            elapsed = time.time() - self.play_time
            wait_time = delay / 1000 - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            
            self.play_time = time.time()
            
            if sound:
                sound_path = os.path.join(os.getcwd(), "assets", sound)
                if os.path.exists(sound_path):
                    try:
                        sound_obj = pygame.mixer.Sound(sound_path)
                        sound_obj.play()
                    except Exception as e:
                        print(f"Ошибка воспроизведения звука: {e}")