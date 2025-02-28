import os
import time
from os import scandir
from os.path import splitext, exists, join
from shutil import move
import pathlib

# ================================= Configuration =================================
sourceDir = 'C:/Users/USERNAME/Downloads'
imageDestDir = 'C:/Users/USERNAME/Downloads/Images'
audioDestDir = 'C:/Users/USERNAME/Downloads/Audio'
videoDestDir = 'C:/Users/USERNAME/Downloads/Video'
docDestDir = 'C:/Users/USERNAME/Downloads/Docs'
exeDestDir = 'C:/Users/USERNAME/Downloads/Executables'
archiveDestDir = 'C:/Users/USERNAME/Downloads/Archives'

# Create destination directories if missing
os.makedirs(imageDestDir, exist_ok=True)
os.makedirs(audioDestDir, exist_ok=True)
os.makedirs(videoDestDir, exist_ok=True)
os.makedirs(docDestDir, exist_ok=True)
os.makedirs(exeDestDir, exist_ok=True)
os.makedirs(archiveDestDir, exist_ok=True)

# File type definitions
audio_ext = {'.wav', '.wma', '.aac', '.mp3', '.flac', '.m4a', '.ogg', '.alac'}
video_ext = {'.webm', '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.mp4', '.m4p', '.m4v', 
             '.avi', '.wmv', '.mov', '.qt', '.flv', '.swf', '.avchd'}
doc_ext = {'.doc', '.docx', '.pdf'}
image_ext = {'.png', '.jpeg', '.jpg', '.jfi', '.jpe', '.jif', '.jfif', 
             '.heif', '.heic', '.gif', '.svg', '.svgz', '.eps', '.webp', 
             '.tiff', '.tif', '.ind', '.ai', '.psd'}
exe_ext = {'.exe'}
archive_ext = {'.zip', '.rar', '.7z'}

# ================================= Core Logic =================================
def organize_files():
    """Run one-time organization of download folder"""
    with scandir(sourceDir) as entries:
        for entry in entries:
            if entry.is_dir():
                continue
            
            file_path = pathlib.Path(entry.name)
            ext = file_path.suffix.lower()
            
            # Skip temporary download files
            if ext in {'.crdownload', '.download', '.tmp'}:
                continue
                
            # Determine destination based on file extension
            dest = None
            if ext in audio_ext:
                dest = audioDestDir
            elif ext in video_ext:
                dest = videoDestDir
            elif ext in doc_ext:
                dest = docDestDir
            elif ext in image_ext:
                dest = imageDestDir
            elif ext in exe_ext:
                dest = exeDestDir
            elif ext in archive_ext:
                dest = archiveDestDir
                
            if dest:
                move_file_safe(dest, sourceDir, entry.name)

def move_file_safe(dest_dir, src_dir, filename):
    """Safely move file with rename if duplicate exists"""
    src_path = pathlib.Path(src_dir) / filename
    dest_path = pathlib.Path(dest_dir) / filename
    
    if not dest_path.exists():
        dest_path.parent.mkdir(exist_ok=True)
        move(str(src_path), str(dest_path))
    else:
        base = src_path.stem
        ext = src_path.suffix
        counter = 1
        while True:
            new_name = f"{base} ({counter}){ext}"
            new_dest = dest_path.parent / new_name
            if not new_dest.exists():
                move(str(src_path), str(new_dest))
                break
            counter += 1

# ================================= Execution =================================
if __name__ == "__main__":
    # Wait 60 seconds after startup to ensure system is ready
    time.sleep(60)
    
    # Run organization once
    organize_files()
    
    # Optional: Add notification sound when done
    # import winsound
    # winsound.Beep(1000, 200)
