import json
import os
import base64
import asyncio
import aiohttp
from utils.logger import Logger
from models.data_models import GiftData

class GiftService:
    def __init__(self):
        self.logger = Logger().get_logger('GiftService')
        self.logger.info("Инициализация сервиса подарков")
        
        self.store_name = "giftinfos.json"
        self.gift_dict = {}
        
        if os.path.exists(self.store_name):
            try:
                with open(self.store_name, 'r') as f:
                    self.gift_dict = json.load(f)
                self.logger.debug(f"Загружено {len(self.gift_dict)} подарков из {self.store_name}")
            except json.JSONDecodeError:
                self.logger.error(f"Ошибка в формате JSON файла {self.store_name}")
                self.gift_dict = {}
    
    def list(self):
        gifts = [
            GiftData(
                id=int(gift_id),
                name=gift_data.get('name', ''),
                image=gift_data.get('image', '')
            )
            for gift_id, gift_data in self.gift_dict.items()
        ]
        self.logger.debug(f"Запрошен список подарков, возвращено {len(gifts)} записей")
        return gifts
    
    def find(self, gift_id):
        gift_id_str = str(gift_id)
        if gift_id_str in self.gift_dict:
            gift_data = self.gift_dict[gift_id_str]
            gift = GiftData(
                id=int(gift_id),
                name=gift_data.get('name', ''),
                image=gift_data.get('image', '')
            )
            self.logger.debug(f"Найден подарок с ID {gift_id}: {gift_data.get('name', '')}")
            return gift
        
        self.logger.debug(f"Подарок с ID {gift_id} не найден")
        return None
    
    async def create(self, gift_id, name, url):
        self.logger.info(f"Создание подарка: ID {gift_id}, название: {name}, URL: {url}")
        try:
            # Используем aiohttp для асинхронного запроса
            async with aiohttp.ClientSession() as session:
                self.logger.debug(f"Загрузка изображения с {url}")
                async with session.get(url) as response:
                    if response.status != 200:
                        self.logger.error(f"Ошибка при загрузке изображения: статус {response.status}")
                        return None
                    
                    content = await response.read()
                    image_data = base64.b64encode(content).decode('utf-8')
                    self.logger.debug(f"Изображение загружено и закодировано в base64")
                    
                    gift_data = {
                        'name': name,
                        'image': image_data
                    }
                    
                    self.gift_dict[str(gift_id)] = gift_data
                    
                    # Сохраняем в файл асинхронно
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self._save_to_file)
                    self.logger.info(f"Подарок ID {gift_id} успешно создан и сохранен")
                    
                    return GiftData(id=gift_id, name=name, image=image_data)
        except Exception as e:
            self.logger.error(f"Ошибка при создании данных подарка: {str(e)}", exc_info=True)
            return None
    
    def _save_to_file(self):
        """Вспомогательный метод для сохранения словаря в файл"""
        try:
            with open(self.store_name, 'w') as f:
                json.dump(self.gift_dict, f)
            self.logger.debug(f"Данные сохранены в {self.store_name}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении данных в файл: {str(e)}")