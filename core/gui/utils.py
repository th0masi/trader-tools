import shutil
import subprocess
import sys
from typing import List


def open_links_in_fresh_window(urls: List[str]) -> bool:
    """Пытается открыть все ссылки в одном НОВОМ окне выбранного браузера."""
    if not urls:
        return False
    candidates = [
        ("chrome", ["--new-window"]), ("google-chrome", ["--new-window"]),
        ("chromium", ["--new-window"]), ("brave", ["--new-window"]),
        ("msedge", ["--new-window"]), ("microsoft-edge", ["--new-window"]),
        ("firefox", ["-new-window"]),
    ]
    for exe, flags in candidates:
        path = shutil.which(exe)
        if path:
            try:
                subprocess.Popen([path, *flags, *urls])
                return True
            except Exception:
                pass
    if sys.platform == "darwin":
        mac_apps = [
            ("Google Chrome", "--new-window"), ("Microsoft Edge", "--new-window"),
            ("Brave Browser", "--new-window"), ("Firefox", "-new-window"),
        ]
        for app, flag in mac_apps:
            try:
                subprocess.Popen(["/usr/bin/open", "-a", app, "--args", flag, *urls])
                return True
            except Exception:
                pass
    return False


def open_links_in_tabs(urls: List[str]) -> bool:
    """Открывает ссылки во вкладках существующего окна браузера (без форс-нового окна)."""
    if not urls:
        return False
    candidates = [
        ("chrome", []), ("google-chrome", []),
        ("chromium", []), ("brave", []),
        ("msedge", []), ("microsoft-edge", []),
        ("firefox", []),
    ]
    for exe, flags in candidates:
        path = shutil.which(exe)
        if path:
            try:
                subprocess.Popen([path, *flags, *urls])
                return True
            except Exception:
                pass
    if sys.platform == "darwin":
        # На macOS оставим дефолтное поведение: откроется в текущем окне/вкладках
        for url in urls:
            try:
                subprocess.Popen(["/usr/bin/open", url])
            except Exception:
                pass
        return True
    return False


