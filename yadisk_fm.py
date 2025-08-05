#!/usr/bin/env python3

import sys
from colorama import init, Fore, Style
from yandex_disk_client import YandexDiskClient
from console_interface import ConsoleInterface
from file_downloader import FileDownloader

init(autoreset=True)


def main():
    try:
        print(f"{Fore.CYAN}Подключение к Яндекс.Диску...{Style.RESET_ALL}")
        client = YandexDiskClient()
        interface = ConsoleInterface(client.client)
        downloader = FileDownloader(client)
        
        # Устанавливаем начальный путь как disk:/
        interface.current_path = 'disk:/'
        
        print(f"{Fore.GREEN}✓ Подключение успешно!{Style.RESET_ALL}\n")
        
        while True:
            interface.display_header()
            
            items = client.list_files(interface.current_path)
            sorted_items = interface.display_files(items)
            interface.display_menu()
            
            command = input(f"{Fore.CYAN}Введите команду: {Style.RESET_ALL}").strip().lower()
            
            if command == 'q':
                print(f"\n{Fore.YELLOW}До свидания!{Style.RESET_ALL}")
                break
            
            elif command == '..':
                interface.go_back()
            
            elif command == 'r':
                continue
            
            elif command.isdigit():
                number = int(command)
                item = interface.get_item_by_number(sorted_items, number)
                
                if item:
                    if item.type == 'dir':
                        new_path = item.path
                        interface.navigate_to(new_path)
                    else:
                        print(f"\n{Fore.YELLOW}Скачать файл '{item.name}'? (y/n): {Style.RESET_ALL}", end='')
                        if input().strip().lower() == 'y':
                            downloader.download_file(item.path, item.name)
                            input(f"\n{Fore.CYAN}Нажмите Enter для продолжения...{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Неверный номер элемента{Style.RESET_ALL}")
                    input(f"\n{Fore.CYAN}Нажмите Enter для продолжения...{Style.RESET_ALL}")
            
            elif command == 'm':
                if not any(item.type == 'file' for item in sorted_items):
                    print(f"{Fore.YELLOW}В этой папке нет файлов для скачивания{Style.RESET_ALL}")
                    input(f"\n{Fore.CYAN}Нажмите Enter для продолжения...{Style.RESET_ALL}")
                    continue
                
                print(f"\n{Fore.CYAN}Режим множественного выбора{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Доступные команды:{Style.RESET_ALL}")
                print(f"  - Введите номера файлов через пробел (например: 3 5 7)")
                print(f"  - Введите диапазон через дефис (например: 3-7)")
                print(f"  - Введите 'all' для выбора всех файлов")
                print(f"  - Введите 'cancel' для отмены")
                print()
                print(f"{Fore.CYAN}Ваш выбор: {Style.RESET_ALL}", end='')
                
                choice = input().strip().lower()
                
                if choice == 'cancel':
                    continue
                
                files_to_download = []
                
                if choice == 'all':
                    for item in sorted_items:
                        if item.type == 'file':
                            files_to_download.append((item.path, item.name))
                else:
                    try:
                        selected_numbers = []
                        
                        # Обработка ввода
                        parts = choice.replace(',', ' ').split()
                        for part in parts:
                            if '-' in part and not part.startswith('-'):
                                # Обработка диапазона
                                start, end = part.split('-')
                                start, end = int(start), int(end)
                                selected_numbers.extend(range(start, end + 1))
                            else:
                                # Обработка одиночного числа
                                selected_numbers.append(int(part))
                        
                        # Удаление дубликатов и сортировка
                        selected_numbers = sorted(set(selected_numbers))
                        
                        for num in selected_numbers:
                            item = interface.get_item_by_number(sorted_items, num)
                            if item and item.type == 'file':
                                files_to_download.append((item.path, item.name))
                            elif item and item.type == 'dir':
                                print(f"{Fore.YELLOW}Пропускаю папку: {item.name}{Style.RESET_ALL}")
                            elif not item:
                                print(f"{Fore.YELLOW}Пропускаю несуществующий номер: {num}{Style.RESET_ALL}")
                    
                    except ValueError:
                        print(f"{Fore.RED}Неверный формат ввода{Style.RESET_ALL}")
                        input(f"\n{Fore.CYAN}Нажмите Enter для продолжения...{Style.RESET_ALL}")
                        continue
                
                if files_to_download:
                    print(f"\n{Fore.CYAN}Выбрано файлов: {len(files_to_download)}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Начать скачивание? (y/n): {Style.RESET_ALL}", end='')
                    if input().strip().lower() == 'y':
                        downloader.download_multiple_files(files_to_download)
                else:
                    print(f"{Fore.YELLOW}Файлы для скачивания не выбраны{Style.RESET_ALL}")
                
                input(f"\n{Fore.CYAN}Нажмите Enter для продолжения...{Style.RESET_ALL}")
            
            else:
                print(f"{Fore.RED}Неизвестная команда{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Нажмите Enter для продолжения...{Style.RESET_ALL}")
    
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Прервано пользователем{Style.RESET_ALL}")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n{Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()