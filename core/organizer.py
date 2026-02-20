import os
import time
import shutil
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

from core.config import WATCH_DIR, FILE_CATEGORIES, HANDLE_DUPLICATES
from utils.file_utils import resolve_duplicate

class DirOrganizer:
    def __init__(self, watch_dir=WATCH_DIR, gui_app=None):
        self.watch_dir = watch_dir
        self.gui_app = gui_app
        self.observer = PollingObserver()
        self.handler = DirOrganizerHandler(self.watch_dir, self.gui_app)

    def start_gui(self):
        if self.gui_app:
            self.gui_app.log(f"File watcher actively monitoring: {self.watch_dir}", "success")

        self.observer.schedule(self.handler, path=self.watch_dir, recursive=False)
        self.observer.start()

        try:
            while self.gui_app and self.gui_app.is_watching:
                time.sleep(1)
        except Exception:
            if self.gui_app:
                self.gui_app.log("File watcher stopped.", "warning")
            self.observer.stop()
        finally:
            self.observer.join()

    def _classify_existing_files_gui(self):
        if not self.gui_app:
            return

        files = [f for f in os.listdir(self.watch_dir) if os.path.isfile(os.path.join(self.watch_dir, f))]
        total_files = len(files)
        processed_files = 0

        for i, file in enumerate(files, 1):
            if self.gui_app.stop_requested:
                self.gui_app.log(f"Organization stopped. Processed {processed_files} of {total_files} files.", "warning")
                return

            path = os.path.join(self.watch_dir, file)
            self.classify_and_move_gui(path, self.watch_dir)
            processed_files += 1

            if i % 10 == 0:
                self.gui_app.log(f"Progress: {i}/{total_files} files processed...", "info")

        self.gui_app.log(f"Organized {total_files} existing files", "success")

    def classify_and_move_gui(self, file_path, base_dir):
        if not os.path.isfile(file_path) or not self.gui_app:
            return

        file_name = os.path.basename(file_path)
        _, ext = os.path.splitext(file_name)
        ext = ext.lower()

        destination_dir = self._detect_destination(ext, base_dir)
        destination_path = os.path.join(destination_dir, file_name)

        if os.path.dirname(file_path) == destination_dir:
            return

        if HANDLE_DUPLICATES:
            destination_path = resolve_duplicate(destination_path)

        try:
            os.makedirs(destination_dir, exist_ok=True)
            shutil.move(file_path, destination_path)
            self.gui_app.increment_file_count()
            folder_name = os.path.basename(destination_dir)
            self.gui_app.log(f"{file_name} → {folder_name}/", "move")
        except Exception as e:
            self.gui_app.log(f"Error moving {file_name}: {str(e)}", "error")

    @staticmethod
    def _detect_destination(ext, base_dir):
        docs = FILE_CATEGORIES.get("Documents", {})

        for subcat, extensions in docs.items():
            if ext in extensions:
                return os.path.join(base_dir, "Documents", subcat)

        for cat, extensions in FILE_CATEGORIES.items():
            if isinstance(extensions, dict):
                continue
            if ext in extensions:
                return os.path.join(base_dir, cat)

        return os.path.join(base_dir, "Others")


class DirOrganizerHandler(FileSystemEventHandler):
    def __init__(self, base_dir, gui_app):
        super().__init__()
        self.base_dir = base_dir
        self.gui_app = gui_app

    def on_created(self, event):
        if event.is_directory:
            return

        temp_exts = FILE_CATEGORIES.get("Temp", [])
        if any(event.src_path.endswith(ext) for ext in temp_exts):
            return

        # Safe file — classify normally with GUI updates
        time.sleep(0.5)  # Give time for file to be completely written
        if self.gui_app and self.gui_app.is_watching:
            self._process_file_with_gui(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return

        temp_exts = FILE_CATEGORIES.get("Temp", [])
        if any(event.dest_path.endswith(ext) for ext in temp_exts):
            return

        if self.gui_app and self.gui_app.is_watching:
            self._process_file_with_gui(event.dest_path)

    def _process_file_with_gui(self, file_path):
        if not os.path.isfile(file_path):
            return

        file_name = os.path.basename(file_path)
        _, ext = os.path.splitext(file_name)
        ext = ext.lower()

        destination_dir = DirOrganizer._detect_destination(ext, self.base_dir)
        destination_path = os.path.join(destination_dir, file_name)

        if os.path.dirname(file_path) == destination_dir:
            return

        if HANDLE_DUPLICATES:
            destination_path = resolve_duplicate(destination_path)

        try:
            os.makedirs(destination_dir, exist_ok=True)
            shutil.move(file_path, destination_path)
            self.gui_app.increment_file_count()
            folder_name = os.path.basename(destination_dir)
            self.gui_app.log(f"{file_name} → {folder_name}/", "move")
        except Exception as e:
            self.gui_app.log(f"Error moving {file_name}: {str(e)}", "error")
