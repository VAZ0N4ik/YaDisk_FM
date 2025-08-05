import os
from colorama import init, Fore, Style, Back
from datetime import datetime

init(autoreset=True)


class ConsoleInterface:
    def __init__(self, client):
        self.client = client
        self.current_path = '/'
        self.path_history = []
    
    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def display_header(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Back.BLUE}{Fore.WHITE} Яндекс.Диск Файловый Менеджер {Style.RESET_ALL}")
        print(f"{Fore.CYAN}Текущий путь: {self.current_path}{Style.RESET_ALL}")
        print("=" * 80)
    
    def display_files(self, items):
        if not items:
            print(f"{Fore.YELLOW}Папка пуста{Style.RESET_ALL}")
            return []
        
        print(f"\n{'Тип':<8} {'Название':<40} {'Размер':<12} {'Изменен':<20}")
        print("-" * 80)
        
        folders = []
        files = []
        
        for item in items:
            if item.type == 'dir':
                folders.append(item)
            else:
                files.append(item)
        
        # Сортировка по убыванию даты изменения (самые новые первыми)
        folders.sort(key=lambda x: x.modified, reverse=True)
        files.sort(key=lambda x: x.modified, reverse=True)
        
        # Создаем отсортированный список всех элементов
        sorted_items = folders + files
        
        for i, item in enumerate(sorted_items, 1):
            if item.type == 'dir':
                modified = item.modified.strftime("%Y-%m-%d %H:%M")
                print(f"{Fore.YELLOW}[DIR]{Style.RESET_ALL}    {i:2d}. {item.name:<35} {'--':<10} {modified}")
            else:
                size = self.format_size(item.size)
                modified = item.modified.strftime("%Y-%m-%d %H:%M")
                print(f"{Fore.GREEN}[FILE]{Style.RESET_ALL}   {i:2d}. {item.name:<35} {size:<10} {modified}")
        
        return sorted_items
    
    def display_menu(self):
        print(f"\n{Fore.CYAN}Команды:{Style.RESET_ALL}")
        print("  [номер] - открыть папку или скачать файл")
        print("  [m] - режим множественного выбора файлов")
        print("  [..] - вернуться в родительскую папку")
        print("  [r] - обновить")
        print("  [q] - выход")
        print()
    
    def navigate_to(self, path):
        if path != self.current_path:
            self.path_history.append(self.current_path)
        self.current_path = path
    
    def go_back(self):
        if self.current_path == '/' or self.current_path == 'disk:/':
            print(f"{Fore.YELLOW}Вы находитесь в корневой папке{Style.RESET_ALL}")
            return False
        
        # Обработка путей вида "disk:/folder" 
        if self.current_path.startswith('disk:/'):
            parts = self.current_path[6:].rstrip('/').split('/')
            if len(parts) <= 1 or (len(parts) == 1 and parts[0] == ''):
                self.current_path = 'disk:/'
            else:
                parent_path = 'disk:/' + '/'.join(parts[:-1])
                self.current_path = parent_path
        else:
            # Обработка обычных путей
            parts = self.current_path.rstrip('/').split('/')
            if len(parts) <= 1:
                self.current_path = '/'
            else:
                parent_path = '/'.join(parts[:-1])
                if not parent_path:
                    parent_path = '/'
                self.current_path = parent_path
        
        return True
    
    def get_item_by_number(self, items, number):
        if 1 <= number <= len(items):
            return items[number - 1]
        return None