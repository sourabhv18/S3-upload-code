import os
import time
import logging
from logging.handlers import RotatingFileHandler
import boto3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURATION ---
WATCH_DIRECTORY = r"D:\Upload_to_S3"
BUCKET_NAME = "uploadfromloq"
S3_PREFIX = "Files/" 
LOG_FILE_NAME = "s3_watcher.log"

# --- LOGGING SETUP ---
# Resolves the directory where this script is running to save the log file there
# --- LOGGING SETUP ---
LOG_DIR = r"D:\Coding\IngestionfromAPI"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE_NAME)

# Ensure the folder actually exists
os.makedirs(LOG_DIR, exist_ok=True)

log_handler = RotatingFileHandler(LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=3)
logging.basicConfig(
    handlers=[log_handler, logging.StreamHandler()],
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
s3_client = boto3.client('s3')

def upload_and_delete(local_path, file_name):
    """Helper function to upload a file to S3 and delete it locally."""
    s3_key = os.path.join(S3_PREFIX, file_name).replace("\\", "/")
    
    # Wait a brief moment to ensure the file is completely written/copied
    time.sleep(1) 
    
    try:
        logging.info(f"Starting upload for: {file_name}")
        s3_client.upload_file(local_path, BUCKET_NAME, s3_key)
        logging.info(f"Successfully uploaded {file_name} to S3. Deleting local copy...")
        os.remove(local_path)
        logging.info(f"Successfully deleted local copy of {file_name}.")
    except Exception as e:
        logging.error(f"Error processing {file_name}: {e}", exc_info=True)

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        local_path = event.src_path
        file_name = os.path.basename(local_path)
        upload_and_delete(local_path, file_name)

if __name__ == "__main__":
    logging.info("S3 Watcher service initialized.")
    
    # 1. PROCESS EXISTING FILES FIRST
    logging.info("Checking for files already existing in the folder...")
    if os.path.exists(WATCH_DIRECTORY):
        for file_name in os.listdir(WATCH_DIRECTORY):
            local_path = os.path.join(WATCH_DIRECTORY, file_name)
            if os.path.isfile(local_path):
                logging.info(f"Found existing file on startup: {file_name}")
                upload_and_delete(local_path, file_name)
    else:
        logging.error(f"The directory {WATCH_DIRECTORY} does not exist.")

    # 2. START WATCHING FOR FUTURE NEW FILES
    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_DIRECTORY, recursive=False)
    observer.start()
    logging.info(f"Watching folder: {WATCH_DIRECTORY} for new files...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Watcher service stopped manually.")
        observer.stop()
    observer.join()

