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
    directory_to_watch = r"\\tcspd40\ME\20240916"  # Directory you want to monitor
    file_monitor = FileMonitor(directory_to_watch)

    try:
        file_monitor.start()
        print(f"Monitoring directory: {directory_to_watch}")

        while True:
            new_files = file_monitor.get_new_files()

            if new_files:
                process_new_files(new_files)

            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping file monitor...")
        file_monitor.stop()

if __name__ == "__main__":
    main()
