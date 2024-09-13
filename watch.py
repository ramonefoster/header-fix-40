from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from queue import Queue

# Custom event handler for file creation
class NewFileHandler(FileSystemEventHandler):
    def __init__(self, file_queue):
        super().__init__()
        self.file_queue = file_queue

    def on_created(self, event):
        if not event.is_directory:
            self.file_queue.put(event.src_path)

# File monitor class to handle watchdog observer
class FileMonitor:
    def __init__(self, directory_to_watch):
        self.directory_to_watch = directory_to_watch
        self.file_queue = Queue()  
        self.event_handler = NewFileHandler(self.file_queue)
        self.observer = Observer()

    def start(self):
        self.observer.schedule(self.event_handler, self.directory_to_watch, recursive=True)
        self.observer.daemon = True
        self.observer.start()
        
    def stop(self):
        # Stop the observer
        self.observer.stop()
        self.observer.join()

    def get_new_files(self):
        # Return a list of new files added to the queue (if any)
        files = []
        while not self.file_queue.empty():
            files.append(self.file_queue.get())
        return files
