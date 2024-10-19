import os
import base64
from io import BytesIO
from PIL import Image
from telethon import TelegramClient, events
from telethon.tl.types import User

from models.content import Content


class TelegramService:
    def __init__(self, api_id, api_hash, session_name):
        self.client = TelegramClient(session_name, api_id, api_hash)

    async def authenticate(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            phone_number = input("Enter your phone number for authentication: ")
            await self.client.send_code_request(phone_number)
            code = input("Enter the code: ")
            await self.client.sign_in(phone_number, code)

    async def list_groups(self):
        groups = []
        offset_id = 0
        last_offset_id = None
        max_iterations = 10
        iteration_count = 0

        while True:
            dialogs = await self.client.get_dialogs(offset_id=offset_id, limit=100)
            if not dialogs:
                break

            for dialog in dialogs:
                if dialog.is_group:
                    groups.append(dialog)

            last_message_id = dialogs[-1].message.id if dialogs[-1].message else None
            if last_message_id:
                offset_id = last_message_id
            else:
                break
            if offset_id == last_offset_id:
                break

            last_offset_id = offset_id
            iteration_count += 1
            if iteration_count >= max_iterations:
                break
        return groups

    async def get_group_by_at(self, username):
        try:
            return await self.client.get_input_entity(username)
        except Exception as e:
            print(f"Error fetching group by username: {e}")
            return None

    async def mirror_group_messages(self, group_id, discord_service):
        save_folder = "profile_image"
        os.makedirs(save_folder, exist_ok=True)
        async with self.client:
            @self.client.on(events.NewMessage(chats=group_id))
            async def handler(event):
                send_image = False
                message_text = event.message.message
                user = await event.get_sender()

                if message_text and isinstance(user, User):
                    user_name = user.username
                    photo_path = os.path.join(save_folder, f"{user_name}_profile.jpg")
                    test =await self.client.download_profile_photo(user, file=photo_path)

                    base64_image = self.convert_image_to_base64(photo_path)
                    payload = Content(message_text, user_name)
                    image_data_url = f"data:image/jpg;base64,{base64_image}"
                    try:
                        send_image = await discord_service.send_message2(payload.format_payload(), image_data_url)
                        if send_image and os.path.exists(photo_path):
                            os.remove(photo_path)
                    except Exception as e:
                        print(f"Error to send message to discord: {e}")
                        if os.path.exists(photo_path):
                            os.remove(photo_path)
                    else:
                        if send_image and os.path.exists(photo_path):
                            os.remove(photo_path)

            print(f"Mirroring messages from group {group_id}. Press Ctrl+C to stop.")
            await self.client.run_until_disconnected()

    def convert_image_to_base64(self, image_path, max_size=(128, 128)):
        if not os.path.exists(image_path):
            print(f"Image {image_path} not found.")
            return None
        try:
            with Image.open(image_path) as img:
                img.thumbnail(max_size)
                buffered = BytesIO()
                img.save(buffered, format="PNG")  # Save as PNG for better quality
                return base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error converting image to Base64: {e}")
            return None
