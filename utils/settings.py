import json
import os
import aiofiles
import asyncio

class Settings:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(cls._instance._load_settings())
            else:
                asyncio.run(cls._instance._load_settings())
        return cls._instance
    
    async def _load_settings(self):
        self.settings_file = "settings.json"
        if os.path.exists(self.settings_file):
            async with aiofiles.open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.loads(await f.read())
        else:
            settings = {}
            
        # Установка значений по умолчанию
        self.user_id = settings.get("user_id", "")
        self.notify_gift = settings.get("notify_gift", True)
        self.speech_gift = settings.get("speech_gift", False)
        self.speech_like = settings.get("speech_like", False)
        self.speech_member = settings.get("speech_member", False)
        self.speech_voice = settings.get("speech_voice", "")
        self.speech_rate = settings.get("speech_rate", 4)
        self.notify_delay = settings.get("notify_delay", 500)
        self.join_text = settings.get("join_text", "@name подключился к стриму")
        self.like_text = settings.get("like_text", "@name поставил лайк")
        self.logging_level = settings.get("logging_level", "DEBUG")  # Добавлен параметр уровня логирования
    
    async def save(self):
        settings = {
            "user_id": self.user_id,
            "notify_gift": self.notify_gift,
            "speech_gift": self.speech_gift,
            "speech_like": self.speech_like,
            "speech_member": self.speech_member,
            "speech_voice": self.speech_voice,
            "speech_rate": self.speech_rate,
            "notify_delay": self.notify_delay,
            "join_text": self.join_text,
            "like_text": self.like_text,
            "logging_level": self.logging_level
        }
        
        async with aiofiles.open(self.settings_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(settings, ensure_ascii=False, indent=2))
