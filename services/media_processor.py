import logging
import mimetypes

from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

from config import SAVE_FOLDER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MediaProcessor:
    """
    Handles the processing and saving of media files from Telegram messages.

    Attributes:
        save_folder (str): Directory path where media files are saved.
        file_manager: Utility for generating filenames and managing file operations.
    """

    def __init__(self, file_manager):
        self.save_folder = SAVE_FOLDER
        self.file_manager = file_manager

    async def process_media(self, client, event):
        """
        Processes and saves media files from a Telegram message event.

        Determines the media type, assigns an appropriate file extension,
        and downloads the media content to a generated filename.

        Args:
            client: Telethon client used for media download.
            event: Telegram message event containing media.

        Returns:
            str: Path to the saved media file, or None if media type is unsupported.
        """
        if isinstance(event.message.media, MessageMediaDocument):
            mime_type = event.message.media.document.mime_type
        elif isinstance(event.message.media, MessageMediaPhoto):
            mime_type = 'image/jpeg'
        else:
            logger.warning(f"Unsupported media type: {type(event.message.media).__name__}")
            return None
        extension = mimetypes.guess_extension(mime_type) or '.bin'
        media_path = self.file_manager.generate_filename(
            f"{'doc_img' if isinstance(event.message.media, MessageMediaPhoto) else 'doc_file'}_", extension)
        await client.download_media(event.message, file=media_path)
        return media_path
