import json
import os
import base64
import requests
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from models.data_models import GiftData

class GiftService:
    def __init__(self):
        self.store_name = "giftinfos.json"
        self.gift_dict = {}
        
        if os.path.exists(self.store_name):
            try:
                with open(self.store_name, 'r') as f:
                    self.gift_dict = json.load(f)
            except json.JSONDecodeError:
                self.gift_dict = {}
    
    def list(self):
        return [
            GiftData(
                id=int(gift_id),
                name=gift_data.get('name', ''),
                image=gift_data.get('image', '')
            )
            for gift_id, gift_data in self.gift_dict.items()
        ]
    
    def find(self, gift_id):
        gift_id_str = str(gift_id)
        if gift_id_str in self.gift_dict:
            gift_data = self.gift_dict[gift_id_str]
            return GiftData(
                id=int(gift_id),
                name=gift_data.get('name', ''),
                image=gift_data.get('image', '')
            )
        return None
    
    async def create(self, gift_id, name, url):
        try:
            # Используем aiohttp для асинхронного запроса
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    
                    content = await response.read()
                    image_data = base64.b64encode(content).decode('utf-8')
                    
                    gift_data = {
                        'name': name,
                        'image': image_data
                    }
                    
                    self.gift_dict[str(gift_id)] = gift_data
                    
                    # Сохраняем в файл (это блокирующая операция, но обычно быстрая)
                    # Для полной асинхронности можно вынести запись в отдельный поток
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self._save_to_file)
                    
                    return GiftData(id=gift_id, name=name, image=image_data)
        except Exception as e:
            print(f"Ошибка при создании данных подарка: {e}")
            return None
    
    def _save_to_file(self):
        """Вспомогательный метод для сохранения словаря в файл"""
        with open(self.store_name, 'w') as f:
            json.dump(self.gift_dict, f)