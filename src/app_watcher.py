import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class AppEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        subprocess.Popen(['python', 'google_search.py'])

if __name__ == "__main__":
    event_handler = AppEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()