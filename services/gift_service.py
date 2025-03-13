import json
import os
import base64
import requests
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
            response = requests.get(url)
            response.raise_for_status()
            image_data = base64.b64encode(response.content).decode('utf-8')
            
            gift_data = {
                'name': name,
                'image': image_data
            }
            
            self.gift_dict[str(gift_id)] = gift_data
            
            # Сохраняем в файл
            with open(self.store_name, 'w') as f:
                json.dump(self.gift_dict, f)
                
            return GiftData(id=gift_id, name=name, image=image_data)
        except Exception as e:
            print(f"Ошибка при создании данных подарка: {e}")
            return None