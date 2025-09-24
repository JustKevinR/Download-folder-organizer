import os
import time
import json
import subprocess
import sys
from pathlib import Path
from shutil import move

# ============================== Config Loader ==============================
DEFAULT_CONFIG_NAME = "bob.settings.json"
CONFIG_PATH = Path(os.environ.get("BOB_CONFIG", Path(__file__).parent / DEFAULT_CONFIG_NAME))

def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {path}\n"
            "Create it from bob.settings.template.json or set BOB_CONFIG to a valid path."
        )
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    required = ["sourceDir", "destinations"]
    for k in required:
        if k not in cfg:
            raise ValueError(f"Missing required config key: {k}")
    return cfg

CFG = load_config(CONFIG_PATH)

# Paths
sourceDir = Path(CFG["sourceDir"]).expanduser().resolve()
destinations = {k: Path(v).expanduser().resolve() for k, v in CFG["destinations"].items()}

# Icons
ICON_ENABLED = bool(CFG.get("icons", {}).get("enabled", True))
ICON_DIR = (Path(__file__).parent / CFG.get("icons", {}).get("iconDir", "icons")).resolve()
folder_icon_map = CFG.get("icons", {}).get("map", {})

# Startup + toasts
STARTUP_DELAY = int(CFG.get("startup", {}).get("delaySeconds", 60))
ENABLE_TOASTS = bool(CFG.get("startup", {}).get("toasts", True))

# Progress bar settings
PROGRESS_WIDTH = 36

# Exit behavior (for EXE double-click): delay or wait for keypress
EXIT_DELAY = int(CFG.get("exit", {}).get("delaySeconds", 0))
WAIT_FOR_KEY = bool(CFG.get("exit", {}).get("waitForKey", False))

# ============================== File Types =================================
audio_ext = {
    ".wav", ".wma", ".aac", ".mp3", ".flac", ".m4a", ".ogg", ".alac", ".aiff", ".opus"
}
video_ext = {
    ".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".mp4", ".m4p", ".m4v", ".avi",
    ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd", ".mkv", ".ts", ".m2ts", ".3gp"
}
doc_ext = {
    ".pdf", ".txt", ".rtf", ".md", ".doc", ".docx", ".odt",
    ".xls", ".xlsx", ".ods", ".csv",
    ".ppt", ".pptx", ".odp",
    ".epub", ".mobi",
    ".json", ".xml", ".yaml", ".yml", ".ini", ".log"
}
image_ext = {
    ".png", ".jpeg", ".jpg", ".jfi", ".jpe", ".jif", ".jfif",
    ".heif", ".heic", ".gif", ".svg", ".svgz", ".eps", ".webp",
    ".tiff", ".tif", ".indd", ".ai", ".psd", ".bmp", ".ico"
}
exe_ext = {
    ".exe", ".msi", ".bat", ".cmd", ".ps1", ".reg"
}
archive_ext = {
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz", ".tbz2", ".iso", ".cab"
}
code_ext = {
    ".py", ".ipynb", ".js", ".ts", ".jsx", ".tsx", ".html", ".css",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".java", ".kt", ".go",
    ".rs", ".rb", ".php", ".sh", ".sql"
}
font_ext = {
    ".ttf", ".otf", ".woff", ".woff2"
}
torrent_ext = { ".torrent" }
threed_ext = { ".stl", ".obj", ".fbx", ".blend", ".step", ".stp", ".dae", ".gltf", ".glb" }

# More temp/partial download extensions to skip
temp_ext = { ".crdownload", ".download", ".tmp", ".part", ".partial", ".!ut" }

# ============================== Helpers ====================================
def _run_attrib(args):
    try:
        subprocess.run(args, check=False, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def ensure_dirs_and_icons():
    for name, path in destinations.items():
        path.mkdir(parents=True, exist_ok=True)
        maybe_set_folder_icon(name, path)

def maybe_set_folder_icon(name: str, folder: Path):
    """Windows: set a custom folder icon if a matching .ico exists in ICON_DIR.
    Handles existing read-only/hidden/system desktop.ini by clearing attributes before write.
    """
    if not ICON_ENABLED:
        return
    try:
        ico_name = folder_icon_map.get(name)
        if not ico_name:
            return
        ico_path = ICON_DIR / ico_name
        if not ico_path.exists():
            return

        desktop_ini = folder / "desktop.ini"

        # Clear attributes if file exists (to avoid PermissionError)
        if desktop_ini.exists():
            _run_attrib(['attrib', '-r', '-s', '-h', str(desktop_ini)])

        ini_content = (
            "[.ShellClassInfo]\n"
            f"IconResource={ico_path},0\n"
            f"IconFile={ico_path}\n"
            "IconIndex=0\n"
        )

        # Ensure it's writable at the OS level too
        try:
            os.chmod(desktop_ini if desktop_ini.exists() else folder, 0o666)
        except Exception:
            pass

        # Write the file
        with open(desktop_ini, "w", encoding="utf-8") as f:
            f.write(ini_content)

        # Re-apply attributes so Explorer uses it and hides it
        _run_attrib(['attrib', '+h', '+s', str(desktop_ini)])
        _run_attrib(['attrib', '+r', str(folder)])  # special folder flag for custom icon
    except PermissionError as e:
        print(f"[icon] Could not set icon for {folder}: Permission denied ({e}). "
              "Try closing Explorer windows pointing to this folder, then re-run as the same Windows user.")
    except Exception as e:
        print(f"[icon] Could not set icon for {folder}: {e}")

def classify(ext: str):
    if ext in audio_ext:   return "Audio"
    if ext in video_ext:   return "Video"
    if ext in doc_ext:     return "Docs"
    if ext in image_ext:   return "Images"
    if ext in exe_ext:     return "Executables"
    if ext in archive_ext: return "Archives"
    if ext in code_ext:    return "Code"
    if ext in font_ext:    return "Fonts"
    if ext in torrent_ext: return "Torrents"
    if ext in threed_ext:  return "3D"
    return None

def move_file_safe(src: Path, dest_dir: Path) -> Path:
    dest = dest_dir / src.name
    if not dest.exists():
        move(str(src), str(dest))
        return dest
    # Deduplicate
    base = src.stem
    ext = src.suffix
    counter = 1
    while True:
        new_dest = dest_dir / f"{base} ({counter}){ext}"
        if not new_dest.exists():
            move(str(src), str(new_dest))
            return new_dest
        counter += 1

def toast(title: str, msg: str):
    if not ENABLE_TOASTS:
        return
    try:
        from win10toast import ToastNotifier  # pip install win10toast
        ToastNotifier().show_toast(title, msg, duration=5, threaded=False)
    except Exception:
        print(f"[{title}] {msg}")

# ------------------------------ Progress Bar -------------------------------
def _print_progress(current: int, total: int, width: int = PROGRESS_WIDTH):
    if total <= 0:
        return
    ratio = current / total
    filled = int(ratio * width)
    bar = "#" * filled + "-" * (width - filled)
    msg = f"\r[Bob] Sorting: |{bar}| {current}/{total}"
    sys.stdout.write(msg)
    sys.stdout.flush()
    if current == total:
        sys.stdout.write("\n")

# ------------------------------ Exit Hold ----------------------------------
def _exit_hold():
    """When packaged as an EXE, keep the window open briefly or until keypress,
    so you can read confirmations.
    """
    try:
        # Only bother if running in a frozen app OR not attached to a TTY
        frozen = getattr(sys, 'frozen', False)
        has_tty = False
        try:
            has_tty = sys.stdout.isatty()
        except Exception:
            has_tty = False

        if not frozen and has_tty:
            return  # likely running in a terminal; don't block

        if WAIT_FOR_KEY:
            print("\n[Bob] Press any key to exit...")
            try:
                import msvcrt
                msvcrt.getch()
            except Exception:
                input()
        elif EXIT_DELAY > 0:
            print(f"\n[Bob] Closing in {EXIT_DELAY} second(s)...")
            time.sleep(EXIT_DELAY)
    except Exception:
        # Fail-safe: don't crash on exit behavior
        pass

# ============================== Core Logic ==================================
def organize_files() -> dict:
    counts = {name: 0 for name in destinations}

    if not sourceDir.exists():
        print(f"[ERROR] Source directory does not exist: {sourceDir}")
        return counts

    # First pass: build a list of candidate files to process (for progress)
    entries = []
    with os.scandir(sourceDir) as it:
        for entry in it:
            if entry.is_dir():
                continue
            ext = Path(entry.name).suffix.lower()
            if ext in temp_ext or entry.name.lower().endswith(".partial"):
                continue
            if classify(ext) is None:
                continue
            entries.append(entry.name)

    total = len(entries)
    if total:
        print(f"[Bob] Found {total} file(s) to sort. Starting...")
    processed = 0

    # Second pass: move files with progress
    for name in entries:
        src = sourceDir / name
        ext = src.suffix.lower()
        dest_key = classify(ext)
        if not dest_key:
            processed += 1
            _print_progress(processed, total)
            continue
        dest_dir = destinations[dest_key]
        new_path = move_file_safe(src, dest_dir)
        counts[dest_key] += 1
        print(f"→ {name}  ➜  {dest_key}/{new_path.name}")
        processed += 1
        _print_progress(processed, total)

    return counts

# ============================== Execution ===================================
if __name__ == "__main__":
    try:
        if STARTUP_DELAY > 0:
            time.sleep(STARTUP_DELAY)

        ensure_dirs_and_icons()
        counts = organize_files()

        # Per-folder confirmation + summary
        for name, n in counts.items():
            if n:
                print(f"[OK] {name}: sorted {n} file(s).")
                toast("Bob sorter", f"{name}: sorted {n} file(s).")

        total = sum(counts.values())
        if total == 0:
            toast("Bob sorter", "Nothing to sort. All clear!")
            print("[INFO] Nothing to sort.")
        else:
            toast("Bob sorter", f"Done! Moved {total} file(s) across {sum(1 for v in counts.values() if v)} folders.")
            print(f"[DONE] Total moved: {total}")

        _exit_hold()
    except Exception as e:
        print(f"[FATAL] {e}")
        toast("Bob sorter", f"Error: {e}")
        _exit_hold()
