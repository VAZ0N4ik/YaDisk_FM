import yadisk
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style
from tqdm import tqdm

init(autoreset=True)
load_dotenv()


class YandexDiskClient:
    def __init__(self):
        self.token = os.getenv('YANDEX_TOKEN')
        if not self.token:
            raise ValueError(f"{Fore.RED}YANDEX_TOKEN не найден в .env файле")
        
        self.client = yadisk.YaDisk(token=self.token)
        
        if not self.client.check_token():
            raise ValueError(f"{Fore.RED}Неверный токен")
    
    def list_files(self, path='/'):
        try:
            items = list(self.client.listdir(path))
            return items
        except Exception as e:
            print(f"{Fore.RED}Ошибка при получении списка файлов: {e}")
            return []
    
    def download_file(self, path, destination):
        try:
            self.client.download(path, destination)
            return True
        except Exception as e:
            print(f"{Fore.RED}Ошибка при скачивании файла: {e}")
            return False
    
    def download_file_with_progress(self, path, destination, file_size):
        try:
            # Получаем ссылку для скачивания
            download_url = self.client.get_download_link(path)
            
            # Скачиваем с прогресс-баром
            import requests
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # Создаем прогресс-бар
            progress_bar = tqdm(
                total=file_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=os.path.basename(destination),
                bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
            )
            
            # Скачиваем файл по частям
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
            
            progress_bar.close()
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Ошибка при скачивании файла: {e}")
            return False
    
    def get_file_info(self, path):
        try:
            return self.client.get_meta(path)
        except Exception as e:
            print(f"{Fore.RED}Ошибка при получении информации о файле: {e}")
            return None