import os
from telethon import TelegramClient, events
from telethon.tl.types import User
from models.content import Content
from models.user import get_username
from utils.image_to_base64 import convert_image_to_base64
from utils.hash import create_hash

class TelegramService:
    def __init__(self, api_id, api_hash, session_name):
        self.save_folder = "profile_image/"
        self.client = TelegramClient(session_name, api_id, api_hash)

    async def authenticate(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self._perform_authentication()

    async def _perform_authentication(self):
        phone_number = input("Enter your phone number for authentication: ")
        await self.client.send_code_request(phone_number)
        code = input("Enter the code: ")
        await self.client.sign_in(phone_number, code)

    async def list_groups(self):
        groups = []
        offset_id = 0
        max_iterations = 3

        for _ in range(max_iterations):
            dialogs = await self.client.get_dialogs(offset_id=offset_id, limit=100)
            if not dialogs:
                break
            groups.extend(dialog for dialog in dialogs if dialog.is_group)
            offset_id = dialogs[-1].message.id if dialogs[-1].message else None

        return groups

    async def get_group_by_at(self, username):
        try:
            return await self.client.get_input_entity(username)
        except Exception as e:
            print(f"Error fetching group by username: {e}")
            return None

    async def mirror_group_messages(self, group_id, discord_service):
        os.makedirs(self.save_folder, exist_ok=True)
        async with self.client:
            @self.client.on(events.NewMessage(chats=group_id))
            async def handler(event):
                await self._handle_new_message(event, discord_service)

            print(f"Mirroring messages from group {group_id}. Press Ctrl+C to stop.")
            await self.client.run_until_disconnected()

    async def _handle_new_message(self, event, discord_service):
        message_text = event.message.message
        user = await event.get_sender()

        if message_text and isinstance(user, User):
            user_name = get_username(user)
            content = Content(message_text, user_name)
            image_data_url = await self._get_user_image_data(user)

            if event.message.reply_to_msg_id:
                payload = await self._create_reply_payload(event, content)
            else:
                payload = content.format_payload()

            await self._send_to_discord(payload, discord_service, image_data_url)

    async def _get_user_image_data(self, user):
        photo_path = os.path.join(self.save_folder, f"img_{create_hash()}.jpg")
        await self.client.download_profile_photo(user, file=photo_path)
        img = await convert_image_to_base64(photo_path)
        if os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except Exception as e:
                print(f"Error to delete profile image: {e}")
            finally:
                return img

    @staticmethod
    async def _create_reply_payload(event, content):
        original_message = await event.get_reply_message()
        if original_message and original_message.from_id and original_message.from_id.user_id:
            original_user = await original_message.get_sender()
            original_user_name = get_username(original_user)
            original_message_text = original_message.message
            return content.format_payload(original_user_name, original_message_text)
        return content.format_payload()

    @staticmethod
    async def _send_to_discord(payload, discord_service, image_data_url):
        try:
            await discord_service.send_message(payload, image_data_url)
        except Exception as e:
            print(f"Error sending message to discord: {e}")

