from utils.image_to_base64 import convert_image_to_base64


class UserService:
    """
    Handles user-related services, particularly for managing user profile images.

    Attributes:
        file_manager: Manages file operations such as downloading and deleting images.
    """

    def __init__(self, file_manager):
        self.file_manager = file_manager

    async def get_user_image_data(self, client, user, event):
        """
        Downloads the user's profile photo, converts it to base64, and cleans up the downloaded file.

        Args:
            client: The Telegram client used to interact with the Telegram API.
            user: The user object whose profile photo is to be downloaded.
            event: The event context, used for error handling or logging.

        Returns:
            str: Base64 representation of the user's profile photo.
        """
        photo_path = self.file_manager.generate_filename('img', '.jpg')
        await client.download_profile_photo(user, file=photo_path)
        img = await convert_image_to_base64(photo_path)
        self.file_manager.delete_file(photo_path, event)
        return img
