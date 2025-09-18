import keyboard
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class HotfolderHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(SUPPORTED_FORMATS):
            self.app.pending_files.append(event.src_path)
            print(f"Datei hinzugefügt zur Warteliste: {event.src_path}")

class HotfolderApp:
    def __init__(self, root):
        self.pending_files = []
        self.copies = tk.IntVar(value=1)
        self.listen_for_shortcuts()

    def listen_for_shortcuts(self):
        for i in range(1, 10):
            keyboard.add_hotkey(str(i), lambda i=i: self.set_copies(i))
        keyboard.add_hotkey("d", self.print_pending_files)

    def print_pending_files(self):
        for filepath in self.pending_files:
            for _ in range(self.copies.get()):
                try:
                    win32api.ShellExecute(0, "print", filepath, None, ".", 0)
                    print(f"Datei gedruckt: {filepath}")
                except Exception as e:
                    print(f"Fehler beim Drucken: {e}")
        self.pending_files.clear()
