from utils.image_to_base64 import convert_image_to_base64


class UserService:
    def __init__(self, file_manager):
        self.file_manager = file_manager

    async def get_user_image_data(self, client, user, event):
        photo_path = self.file_manager.generate_filename('img', '.jpg')
        await client.download_profile_photo(user, file=photo_path)
        img = await convert_image_to_base64(photo_path)
        self.file_manager.delete_file(photo_path, event)
        return img
