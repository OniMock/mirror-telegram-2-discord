import mimetypes
import os

import aiohttp
from telethon import TelegramClient, events
from telethon.tl.types import User, MessageMediaPhoto, MessageMediaDocument
from models.content import Content
from models.user import get_username
from utils.image_to_base64 import convert_image_to_base64
from utils.hash import create_hash

class TelegramService:
    def __init__(self, api_id, api_hash, session_name):
        self.save_folder = "profile_files/"
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

    async def _get_user_document(self, event):
        if isinstance(event.message.media, MessageMediaDocument):
            mime_type = event.message.media.document.mime_type
        else:
            mime_type = 'image/jpeg'

        extension = mimetypes.guess_extension(mime_type) or '.bin'
        media_filename = f"{'img' if isinstance(event.message.media, MessageMediaPhoto) else 'file'}_{create_hash()}{extension}"
        media_path = os.path.join(self.save_folder, media_filename)

        await self.client.download_media(event.message, file=media_path)
        return {"path": media_path, "extension": extension}

    async def _handle_new_message(self, event, discord_service):
        message_text = event.message.message or None
        user = await event.get_sender()
        user_name = get_username(user)
        document_path = None
        files = {}
        form_data = aiohttp.FormData()

        user_image_data_url = await self._get_user_image_data(user)
        form_data_message = Content(user_name, user_image_data_url)

        if event.message.media:
            document_path = await self._get_user_document(event)

        if message_text and isinstance(user, User):
            if event.message.reply_to_msg_id:
                if document_path:
                    original_message = await event.get_reply_message()
                    if original_message and original_message.from_id and original_message.from_id.user_id:
                        original_user = await original_message.get_sender()
                        original_user_name = get_username(original_user)
                        original_message_text = original_message.message
                        form_data_message.set_content(message_text)
                        form_data_message.add_embed("*reply*:")
                        form_data_message.add_field(original_user_name, original_message_text, False)
                        form_data_message.set_footer("Powered by Onimock")
                    files['file'] = open(document_path["path"], 'rb')
                else:
                    original_message = await event.get_reply_message()
                    if original_message and original_message.from_id and original_message.from_id.user_id:
                        original_user = await original_message.get_sender()
                        original_user_name = get_username(original_user)
                        original_message_text = original_message.message
                        form_data_message.set_content(message_text)
                        form_data_message.add_embed("*reply*:")
                        form_data_message.add_field(original_user_name, original_message_text, False)
                        form_data_message.set_footer("Powered by Onimock")
            else:
                form_data_message.set_content(message_text)
                if document_path:
                    files['file'] = open(document_path["path"], 'rb')
        elif event.message.media:
            form_data_message.set_content(message_text)
            if document_path:
                files['file'] = open(document_path["path"], 'rb')
        if files:
            form_data.add_field('files', files['file'], filename=document_path["path"].split('/')[-1])
        await self._send_to_discord(form_data_message, form_data, discord_service)

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
    async def _send_to_discord(form_data_message, form_data, discord_service):
        try:
            await discord_service.send_message(form_data_message, form_data)
        except Exception as e:
            print(f"Error sending message to discord: {e}")