from watchdog.observers import Observer
import os
import time
import getpass
from watchdog.events import FileSystemEventHandler

def print_boxed(text):
    """Выводит текст в рамке из символов | и -"""
    lines = text.strip().split('\n')
    max_len = max(len(line) for line in lines)
    border = '+' + '-' * (max_len + 2) + '+'
    print(border)
    for line in lines:
        print(f"| {line.ljust(max_len)} |")
    print(border)

class Handler(FileSystemEventHandler):
    def __init__(self):
        self.folder_mapping = {
            '.zip': 'зип',
            '.7z': 'зип',
            '.rar': 'зип',
            '.tar': 'зип',
            '.gz': 'зип',
            '.exe': 'exe',
            '.msi': 'exe',
            '.iso': 'iso',
            '.img': 'iso',
            '.jpg': 'Изображения',
            '.png': 'Изображения',
            '.mp3': 'музыка',
            '.wav': 'музыка',
            '.flac': 'музыка',
            '.pptx': 'Презентации',
            '.ppt': 'Презентации',
            '.xls': 'excel',
            '.xlsx': 'excel',
            '.doc': 'Документы',
            '.docx': 'Документы',
            '.pdf': 'pdf',
            '.jar': 'minecraft_mods',
            '.torrent': 'torrent',
            '.apk': 'android_apps'
        }
        self.last_processed = {}  # Словарь для отслеживания последних обработанных файлов
        for folder in set(self.folder_mapping.values()):
            os.makedirs(os.path.join(folder_track, folder), exist_ok=True)

    def process_existing_files(self):
        """Обработка существующих файлов при запуске"""
        files = [f for f in os.listdir(folder_track) 
                if os.path.isfile(os.path.join(folder_track, f))]
        
        moved_files = 0
        output_lines = ["File Organizer v1.0", "Мониторинг папки: Downloads", "Проверка файлов в папке..."]
        
        for filename in files:
            src_path = os.path.join(folder_track, filename)
            _, extension = os.path.splitext(filename)
            extension = extension.lower()
            
            if extension in self.folder_mapping:
                dest_folder = os.path.join(folder_track, self.folder_mapping[extension])
                try:
                    os.rename(src_path, os.path.join(dest_folder, filename))
                    moved_files += 1
                    self.last_processed[filename] = time.time()  # Запоминаем время обработки
                except Exception:
                    pass
        
        if moved_files > 0:
            output_lines.append(f"Успешно перемещено {moved_files} файлов")
        else:
            output_lines.append("Все файлы уже отсортированы")
        
        output_lines.extend([
            "Наблюдатель запущен. Мониторинг изменений...",
            "Для остановки нажмите CTRL + C"
        ])
        
        print_boxed('\n'.join(output_lines))
        return moved_files

    def on_modified(self, event):
        """Обработка новых файлов с защитой от дублирования"""
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            current_time = time.time()
            
            # Проверяем, что файл существует и не обрабатывался в последние 2 секунды
            if (os.path.isfile(event.src_path) and (filename not in self.last_processed or current_time - self.last_processed.get(filename, 0) > 2)):
                
                _, extension = os.path.splitext(filename)
                extension = extension.lower()
                
                if extension in self.folder_mapping:
                    dest_folder = self.folder_mapping[extension]
                    dest_path = os.path.join(folder_track, dest_folder, filename)
                    try:
                        os.rename(event.src_path, dest_path)
                        print_boxed(f"Новый файл перемещен:\n{filename} -> {dest_folder}")
                        self.last_processed[filename] = current_time  # Обновляем время обработки
                    except Exception as e:
                        print_boxed(f"Ошибка перемещения:\n{filename}\n{str(e)}")

# Настройки
folder_track = f'C:\\Users\\{getpass.getuser()}\\Downloads'

# Инициализация
handler = Handler()
observer = Observer()
observer.schedule(handler, folder_track, recursive=True)

# Первоначальная обработка
handler.process_existing_files()

# Запуск наблюдателя
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    print_boxed("Наблюдатель остановлен")
observer.join()