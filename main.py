import time
from watch import FileMonitor
from explode import explode_cube

# Function to simulate taking action on new files
def process_new_files(file_paths):
    for file_path in file_paths:
        print(f"New file detected: {file_path}")
        if ".fits" in file_path:
            explode_cube(file_path)

def main():
    directory_to_watch = r"test\sub1"  # Change this to the directory you want to monitor
    file_monitor = FileMonitor(directory_to_watch)

    try:
        # Start the file monitor in a separate thread
        file_monitor.start()
        print(f"Monitoring directory: {directory_to_watch}")

        while True:
            # Get the new files detected by the file monitor
            new_files = file_monitor.get_new_files()

            # Process new files (if any)
            if new_files:
                process_new_files(new_files)

            time.sleep(1)  # Sleep to avoid tight loop

    except KeyboardInterrupt:
        print("Stopping file monitor...")
        file_monitor.stop()

if __name__ == "__main__":
    main()
