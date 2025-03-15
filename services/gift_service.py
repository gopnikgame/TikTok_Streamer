import os
import json
import base64
import aiohttp
import asyncio
from utils.logger import Logger
from utils.error_handler import ErrorHandler
from models.data_models import GiftData

class GiftService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GiftService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Инициализация сервиса подарков"""
        self.logger = Logger().get_logger('GiftService')
        self.error_handler = ErrorHandler()
        self.logger.info("Инициализация сервиса подарков")
        
        self.gift_dict = {}
        self.gift_file = "gifts.json"
        
        # Загружаем данные из файла, если он существует
        self._load_from_file()
    
    def _load_from_file(self):
        """Загружает данные о подарках из файла"""
        try:
            if os.path.exists(self.gift_file):
                with open(self.gift_file, 'r', encoding='utf-8') as f:
                    self.gift_dict = json.load(f)
                self.logger.info(f"Загружено {len(self.gift_dict)} записей о подарках из файла")
            else:
                self.logger.debug(f"Файл {self.gift_file} не найден, инициализация пустого словаря")
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке данных о подарках: {str(e)}", exc_info=True)
            self.error_handler.handle_file_error(None, e, self.gift_file)
            self.gift_dict = {}
    
    def _save_to_file(self):
        """Сохраняет данные о подарках в файл"""
        try:
            with open(self.gift_file, 'w', encoding='utf-8') as f:
                json.dump(self.gift_dict, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Сохранено {len(self.gift_dict)} записей о подарках в файл")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении данных о подарках: {str(e)}", exc_info=True)
            self.error_handler.handle_file_error(None, e, self.gift_file)
    
    def get(self, gift_id):
        """Получает данные подарка по ID"""
        try:
            gift_id_str = str(gift_id)
            
            if gift_id_str in self.gift_dict:
                data = self.gift_dict[gift_id_str]
                self.logger.debug(f"Получены данные подарка ID {gift_id}: {data}")
                return GiftData(id=gift_id, name=data['name'], image=data['image'])
            
            self.logger.debug(f"Данные подарка ID {gift_id} не найдены")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка при получении данных подарка ID {gift_id}: {str(e)}", exc_info=True)
            return None
    
    async def create(self, gift_id, name, url):
        """Создает новую запись о подарке"""
        try:
            self.logger.debug(f"Запуск создания данных подарка ID {gift_id}, имя: {name}, URL: {url}")
            # Используем aiohttp для асинхронного запроса
            async with aiohttp.ClientSession() as session:
                try:
                    self.logger.debug(f"Запрос изображения подарка по URL: {url}")
                    async with session.get(url) as response:
                        if response.status != 200:
                            error_msg = f"Ошибка при загрузке изображения подарка: HTTP {response.status}"
                            self.logger.error(error_msg)
                            return None
                        
                        content = await response.read()
                        image_data = base64.b64encode(content).decode('utf-8')
                        
                        gift_data = {
                            'name': name,
                            'image': image_data
                        }
                        
                        self.gift_dict[str(gift_id)] = gift_data
                        self.logger.debug(f"Данные подарка ID {gift_id} добавлены в словарь: {gift_data}")
                        
                        # Сохраняем в файл асинхронно
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, self._save_to_file)
                        self.logger.info(f"Подарок ID {gift_id} успешно создан и сохранен")
                        
                        return GiftData(id=gift_id, name=name, image=image_data)
                except aiohttp.ClientError as e:
                    self.logger.error(f"Ошибка сети при создании данных подарка: {str(e)}")
                    self.error_handler.handle_network_error(None, e, f"загрузке изображения подарка {gift_id}")
                    return None
        except Exception as e:
            self.logger.error(f"Ошибка при создании данных подарка: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(None, "Ошибка обработки подарка", 
                                              f"Не удалось создать данные для подарка ID {gift_id}", str(e))
            return None
    
    def create_sync(self, gift_id, name, url):
        """Синхронный вариант метода create для использования из других потоков"""
        try:
            self.logger.debug(f"Запуск синхронного создания данных подарка ID {gift_id}, имя: {name}, URL: {url}")
            # Создаем временный event loop для выполнения асинхронного кода
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.create(gift_id, name, url))
            loop.close()
            return result
        except Exception as e:
            self.logger.error(f"Ошибка при синхронном создании данных подарка: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(None, "Ошибка обработки подарка", 
                                              f"Не удалось создать данные для подарка ID {gift_id}", str(e))
            return None
    
    def delete(self, gift_id):
        """Удаляет данные о подарке"""
        try:
            self.logger.debug(f"Запуск удаления данных подарка ID {gift_id}")
            gift_id_str = str(gift_id)
            
            if gift_id_str in self.gift_dict:
                del self.gift_dict[gift_id_str]
                self._save_to_file()
                self.logger.info(f"Данные подарка ID {gift_id} удалены")
                return True
            
            self.logger.debug(f"Попытка удаления несуществующего подарка ID {gift_id}")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при удалении данных подарка: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(None, "Ошибка удаления", 
                                              f"Не удалось удалить данные подарка ID {gift_id}", str(e))
            return False
    
    def get_all(self):
        """Возвращает словарь со всеми данными о подарках"""
        try:
            self.logger.debug("Запуск получения всех данных о подарках")
            result = {}
            
            for gift_id_str, data in self.gift_dict.items():
                gift_id = int(gift_id_str)
                result[gift_id] = GiftData(id=gift_id, name=data['name'], image=data['image'])
            
            self.logger.debug(f"Получен список всех подарков: {len(result)} записей")
            return result
        except Exception as e:
            self.logger.error(f"Ошибка при получении списка подарков: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(None, "Ошибка получения данных", 
                                              "Не удалось получить список всех подарков", str(e))
            return {}
    
    def clear(self):
        """Очищает все данные о подарках"""
        try:
            self.logger.debug("Запуск очистки данных о подарках")
            self.gift_dict = {}
            self._save_to_file()
            self.logger.info("Данные о подарках очищены")
        except Exception as e:
            self.logger.error(f"Ошибка при очистке данных о подарках: {str(e)}", exc_info=True)
            self.error_handler.show_error_dialog(None, "Ошибка очистки данных", 
                                              "Не удалось очистить данные о подарках", str(e))