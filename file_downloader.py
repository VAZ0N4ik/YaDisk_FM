import os
from colorama import init, Fore, Style
from pathlib import Path

init(autoreset=True)


class FileDownloader:
    def __init__(self, client):
        self.client = client
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
    
    def sanitize_filename(self, filename):
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def get_unique_filename(self, filepath):
        base_path = Path(filepath)
        directory = base_path.parent
        stem = base_path.stem
        suffix = base_path.suffix
        
        counter = 1
        new_path = base_path
        
        while new_path.exists():
            new_path = directory / f"{stem} ({counter}){suffix}"
            counter += 1
        
        return new_path
    
    def download_file(self, remote_path, item_name, file_size=None):
        try:
            safe_name = self.sanitize_filename(item_name)
            local_path = self.download_dir / safe_name
            
            if local_path.exists():
                print(f"{Fore.YELLOW}Файл уже существует. Создаю уникальное имя...{Style.RESET_ALL}")
                local_path = self.get_unique_filename(local_path)
            
            print(f"{Fore.CYAN}Скачивание: {item_name}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Сохранение в: {local_path}{Style.RESET_ALL}")
            
            # Если размер файла известен, используем скачивание с прогрессом
            if file_size and file_size > 0:
                success = self.client.download_file_with_progress(remote_path, str(local_path), file_size)
            else:
                success = self.client.download_file(remote_path, str(local_path))
            
            if success:
                actual_size = local_path.stat().st_size
                print(f"{Fore.GREEN}✓ Скачано успешно! Размер: {self.format_size(actual_size)}{Style.RESET_ALL}")
                return True
            else:
                return False
            
        except Exception as e:
            print(f"{Fore.RED}✗ Ошибка при скачивании: {e}{Style.RESET_ALL}")
            return False
    
    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def download_multiple_files(self, files_to_download):
        successful = 0
        failed = 0
        
        print(f"\n{Fore.CYAN}Начинаю скачивание {len(files_to_download)} файлов...{Style.RESET_ALL}\n")
        
        for i, (remote_path, item_name, file_size) in enumerate(files_to_download, 1):
            print(f"{Fore.BLUE}[{i}/{len(files_to_download)}]{Style.RESET_ALL}")
            
            if self.download_file(remote_path, item_name, file_size):
                successful += 1
            else:
                failed += 1
            
            print()
        
        print(f"{Fore.GREEN}Завершено! Успешно: {successful}, Ошибок: {failed}{Style.RESET_ALL}")
        return successful, failed