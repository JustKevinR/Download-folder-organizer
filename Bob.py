import sys
from time import sleep
from os import scandir, rename
from os.path import splitext, exists, join
from shutil import move
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pystray
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image
import pathlib

# Directories and extensions
sourceDir = 'C:/Users/USERNAME/Downloads'
imageDestDir = 'C:/Users/USERNAME/Downloads/Images'
audioDestDir = 'C:/Users/USERNAME/Downloads/Audio'
videoDestDir = 'C:/Users/USERNAME/Downloads/Video'
docDestDir = 'C:/Users/USERNAME/Downloads/Docs'
exeDestDir = 'C:/Users/USERNAME/Downloads/Executables'
archiveDestDir = 'C:/Users/USERNAME/Downloads/Archives'

audioExt = ['.wav', '.wma', '.aac', '.mp3', '.flac', '.m4a', '.ogg', '.alac']
videoExt = ['.webm', '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.mp4', '.m4p', '.m4v', '.avi',
            '.wmv', '.mov', '.qt', '.flv', '.swf', '.avchd']
docExt = ['.doc', '.docx', '.pdf']
imageExt = ['.png', '.jpeg', '.jpg', '.jfi', '.jpe', '.jif', '.jfif', '.heif', '.heic',
            '.gif', '.svg', '.svg2', '.eps', '.webp', '.tiff', '.tif', '.ind', '.ai', '.psd']
exeExt = ['.exe']
archiveExt = ['.zip', '.rar', '7z']


def moveFile(dest, currDir, name):
    """Move a file, renaming if it already exists."""
    file_path = pathlib.Path(name)
    if file_path.suffix in ['.crdownload', '.download', '.tmp']:
        return  # ignore files with these extensions
    new_name = file_path.name
    if exists(join(dest, new_name)):
        base = file_path.stem
        suffix = file_path.suffix
        count = 1
        while exists(join(dest, new_name)):
            new_name = f'{base} ({str(count)}){suffix}'
            count += 1
    oldPath = join(currDir, name)
    newPath = join(dest, new_name)
    move(oldPath, newPath)

class Watcher(FileSystemEventHandler):
    def on_modified(self, _):
        self.clean()
    
    def clean(self):
        with scandir(sourceDir) as entries:
            for entry in entries:
                if entry.is_dir():
                    continue
                # Check audio files
                for ext in audioExt:
                    if entry.name.endswith(ext):
                        moveFile(audioDestDir, sourceDir, entry.name)
                        break
                # Check video files
                for ext in videoExt:
                    if entry.name.endswith(ext):
                        moveFile(videoDestDir, sourceDir, entry.name)
                        break
                # Check document files
                for ext in docExt:
                    if entry.name.endswith(ext):
                        moveFile(docDestDir, sourceDir, entry.name)
                        break
                # Check image files
                for ext in imageExt:
                    if entry.name.endswith(ext):
                        moveFile(imageDestDir, sourceDir, entry.name)
                        break
                # Check executable files
                for ext in exeExt:
                    if entry.name.endswith(ext):
                        moveFile(exeDestDir, sourceDir, entry.name)
                        break
                # Check archive files
                for ext in archiveExt:
                    if entry.name.endswith(ext):
                        moveFile(archiveDestDir, sourceDir, entry.name)
                        break


# Start the observer
watcher = Watcher()
observer = Observer()
observer.schedule(watcher, sourceDir, recursive=True)
observer.start()

try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()

# System Tray Icon
image = Image.new('RGB', (64, 64), 'red')
def stop(icon, _):
    observer.stop()
    observer.join()
    icon.stop()

tray = icon(
    'Computer Cleaner',
    icon=image,
    menu=menu(
        item('Exit', stop))
).run()
