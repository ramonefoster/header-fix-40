import time
import argparse
import os

from watch import FileMonitor
from explode import explode_cube

# Function to simulate taking action on new files
def process_new_files(file_paths, overwrite, processed_files):
    for file_path in file_paths:
        if file_path in processed_files:
            continue  # Skip already processed files        
        if ".fits" in file_path:
            print(f"New file detected: {file_path}")
            file_exploded = explode_cube(file_path, overwrite)
            processed_files.add(file_exploded)  # Add to processed set after processing

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Monitor a directory for new fits files.")
    
    parser.add_argument(
        '--directory', '-d', 
        type=str, 
        default=r"test",  # Default directory if none provided
        help="Directory to monitor for new files. (Default: ./test)"
    )

    parser.add_argument(
        '-o', '--overwrite', 
        action='store_true',  
        help="Overwrite files after changes. (Default: False)"
    )

    parser.add_argument(
        '-x', '--off', 
        action='store_true',  
        help="Overwrite files after changes. (Default: False)"
    )
    
    args = parser.parse_args()

    directory_to_watch = args.directory
    overwrite = args.overwrite
    off = args.off
    file_monitor = FileMonitor(directory_to_watch)
    processed_files = set()  # Set to store processed file paths

    try:
        file_monitor.start()
        
        if off:
            print(f"Exploding cubes on directory: {directory_to_watch}")
            for filename in os.listdir(directory_to_watch):
                full_path = os.path.join(directory_to_watch, filename)
                process_new_files([full_path], overwrite, processed_files)
            
            return

        print(f"Monitoring directory: {directory_to_watch}")
        while True:
            new_files = file_monitor.get_new_files()

            if new_files:
                process_new_files(new_files, overwrite, processed_files)

            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping file monitor...")
        file_monitor.stop()

if __name__ == "__main__":
    main()
