import os
import logging
from config import *

from utils.hash import create_hash

logger = logging.getLogger(__name__)


class FileManager:
    def __init__(self):
        self.base_folder = SAVE_FOLDER
        os.makedirs(SAVE_FOLDER, exist_ok=True)

    @staticmethod
    def open_file_safely(file_path, event):
        """
        Safely opens a file for reading.

        Args:
            file_path (str): The path of the file to open.
            event (Any): The event context for logging errors.

        Returns:
            file: The opened file object, or None if an error occurred.
        """
        try:
            return open(file_path, 'rb')
        except Exception as e:
            logger.error(f"Error opening file {file_path}: {e} - Event:\n{event}")
            return None

    def close_file_safely(self, files, file_path, event):
        """
        Safely closes an opened file and deletes it.

        Args:
            files (dict): A dictionary containing file objects.
            file_path (str): The path of the file to delete.
            event (Any): The event context for logging errors.
        """
        if 'file' in files and files['file']:
            try:
                files['file'].close()
            except Exception as e:
                logger.error(f"Error closing file {file_path}: {e}")
            finally:
                self.delete_file(file_path, event)

    @staticmethod
    def delete_file(file_path, event):
        """
        Deletes a file at the specified path.

        Args:
            file_path (str): The path of the file to delete.
            event (Any): The event context for logging errors.
        """
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e} - Event:\n{event}")

    def generate_filename(self, prefix, extension):
        """
        Generates a unique filename using a prefix and extension.

        Args:
            prefix (str): The prefix for the filename.
            extension (str): The file extension.

        Returns:
            str: The generated filename with a path.
        """
        return os.path.join(self.base_folder, f"{prefix}_{create_hash()}{extension}")
