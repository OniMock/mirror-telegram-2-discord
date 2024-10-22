import os
import logging

from utils.hash import create_hash

logger = logging.getLogger(__name__)


class FileManager:
    def __init__(self, base_folder):
        self.base_folder = base_folder
        os.makedirs(base_folder, exist_ok=True)

    def open_file_safely(self, file_path, event):
        try:
            return open(file_path, 'rb')
        except Exception as e:
            logger.error(f"Error opening file {file_path}: {e} - Event:\n{event}")
            return None

    def close_file_safely(self, files, file_path, event):
        if 'file' in files and files['file']:
            try:
                files['file'].close()
            except Exception as e:
                logger.error(f"Error closing file {file_path}: {e}")
            finally:
                self.delete_file(file_path, event)

    def delete_file(self, file_path, event):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e} - Event:\n{event}")

    def generate_filename(self, prefix, extension):
        return os.path.join(self.base_folder, f"{prefix}_{create_hash()}{extension}")
