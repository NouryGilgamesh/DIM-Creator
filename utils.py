import os
import sys
import subprocess
from contextlib import contextmanager
from PyQt5.QtCore import QStandardPaths, Qt
from qfluentwidgets import InfoBar, InfoBarPosition


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def documents_dir():
    p = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
    return p or os.path.join(os.path.expanduser('~'), 'Documents')


def downloads_dir():
    p = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
    return p or os.path.join(os.path.expanduser('~'), 'Downloads')


DOC_MAIN_DIR = os.path.join(documents_dir(), "DIMCreator")
os.makedirs(DOC_MAIN_DIR, exist_ok=True)


@contextmanager
def suppress_cmd_window():
    if os.name != "nt":
        yield
        return

    original_popen = subprocess.Popen

    si_hidden = subprocess.STARTUPINFO()
    si_hidden.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si_hidden.wShowWindow = subprocess.SW_HIDE

    try:
        def patched_popen(*args, **kwargs):
            flags = kwargs.get("creationflags", 0)
            try:
                C_NEW_CON = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
                DETACHED = getattr(subprocess, "DETACHED_PROCESS", 0)
                C_NO_WIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                if not (flags & (C_NEW_CON | DETACHED)):
                    flags |= C_NO_WIN
            except Exception:
                pass
            kwargs["creationflags"] = flags

            si = kwargs.get("startupinfo")
            if si is None:
                kwargs["startupinfo"] = si_hidden
            else:
                try:
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    si.wShowWindow = subprocess.SW_HIDE
                except Exception:
                    kwargs["startupinfo"] = si_hidden
            return original_popen(*args, **kwargs)

        subprocess.Popen = patched_popen
        yield
    finally:
        subprocess.Popen = original_popen


def get_optimal_workers():
    logical_cores = os.cpu_count() or 1
    suggested_workers = max(2, int(logical_cores * 1.5))
    max_workers_cap = 8
    return min(suggested_workers, max_workers_cap)


def calculate_total_files(directory):
    total_files = 0
    for _, _, files in os.walk(directory):
        total_files += len(files)
    return total_files


tooltip_stylesheet = """\
QToolTip {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #555;
    padding: 4px;
    border-radius: 5px;
    opacity: 200;
    font-size: 9pt;
}
"""

label_stylesheet = """\
QLabel {
    color: white;
    font-family: 'Segoe UI';
    font-size: 10pt;
}
"""


def show_warning(parent, title, content, orient=Qt.Horizontal, position=InfoBarPosition.TOP_RIGHT,
                 closable=True, duration=2000):
    InfoBar.warning(title=title, content=content, orient=orient, isClosable=closable,
                    position=position, duration=duration, parent=parent)


def show_success(parent, title, content, orient=Qt.Horizontal, position=InfoBarPosition.TOP_RIGHT,
                 closable=True, duration=2000):
    InfoBar.success(title=title, content=content, orient=orient, isClosable=closable,
                    position=position, duration=duration, parent=parent)


def show_error(parent, title, content, orient=Qt.Horizontal, position=InfoBarPosition.TOP_RIGHT,
               closable=True, duration=5000):
    InfoBar.error(title=title, content=content, orient=orient, isClosable=closable,
                  position=position, duration=duration, parent=parent)


def show_info(parent, title, content, orient=Qt.Horizontal, position=InfoBarPosition.TOP_RIGHT,
              closable=True, duration=2000):
    InfoBar.info(title=title, content=content, orient=orient, isClosable=closable,
                 position=position, duration=duration, parent=parent)
