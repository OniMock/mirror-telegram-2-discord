import mimetypes
import os
import aiohttp
import logging
from telethon import TelegramClient, events
from telethon.tl.types import User, MessageMediaPhoto, MessageMediaDocument, Channel, MessageMediaPoll
from models.content import Content
from models.embed import Embed
from models.user import get_username
from utils.image_to_base64 import convert_image_to_base64
from utils.hash import create_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self, api_id, api_hash, session_name):
        self.save_folder = "profile_files/"
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.last_user = None

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
        seen_ids = set()
        offset_id = 0
        max_iterations = 6

        async for dialog in self.client.iter_dialogs():
            if dialog.is_channel:
                groups.append(dialog)
                seen_ids.add(dialog.id)

        for _ in range(max_iterations):
            dialogs = await self.client.get_dialogs(offset_id=offset_id, limit=100)
            if not dialogs:
                break

            for dialog in dialogs:
                if dialog.is_group and dialog.id not in seen_ids:
                    groups.append(dialog)
                    seen_ids.add(dialog.id)
            offset_id = dialogs[-1].message.id if dialogs[-1].message else None

        return groups

    async def get_entity_group(self, group):
        try:
            if group.isdigit():
                group = int(group)
            elif group.startswith('@'):
                group = group[1:]
            group_entity = await self.client.get_entity(group)
            return group_entity
        except Exception as e:
            logger.error(f"Error fetching entity group: {e}")
            return None

    async def mirror_group_messages(self, group_id, discord_service):
        os.makedirs(self.save_folder, exist_ok=True)
        async with self.client:
            @self.client.on(events.NewMessage(chats=group_id))
            async def handler(event):
                if not isinstance(event.message.media, MessageMediaPoll):
                    await self._handle_new_message(discord_service, event)

            print(f"Mirroring messages from group {group_id}. Press Ctrl+C to stop.")
            await self.client.run_until_disconnected()

    async def _get_user_document(self, event):
        if isinstance(event.message.media, MessageMediaDocument):
            mime_type = event.message.media.document.mime_type
        else:
            mime_type = 'image/jpeg'

        extension = mimetypes.guess_extension(mime_type) or '.bin'
        media_filename = f"{'doc_img' if isinstance(event.message.media, MessageMediaPhoto) else 'doc_file'}_{create_hash()}{extension}"
        media_path = os.path.join(self.save_folder, media_filename)

        await self.client.download_media(event.message, file=media_path)
        return media_path

    async def _handle_new_message(self, discord_service, event):
        message_text = event.message.message or None
        user = await event.get_sender() or event.chat

        user_name = get_username(user)
        document_path = None
        files = {}
        form_data = aiohttp.FormData()
        embed = Embed('*reply*:')

        user_image_data_url = await self._get_user_image_data(user, event)
        form_data_message = Content(user_name)

        if event.message.media:
            document_path = await self._get_user_document(event)

        if message_text:
            form_data_message.set_content(message_text)

        if event.message.reply_to_msg_id:
            await self._handle_reply(form_data_message, embed, event)

        if document_path:
            self._open_file_safely(files, document_path, event)

        if files:
            form_data.add_field('files', files['file'], filename=document_path.split('/')[-1])
        self.update_webhook_avatar(user_name, user_image_data_url, form_data_message)
        try:
            await self._send_to_discord(form_data_message, form_data, discord_service, event)
        finally:
            self._close_file_safely(files, document_path, event)

    async def _get_user_image_data(self, user, event):
        photo_path = os.path.join(self.save_folder, f"img_{create_hash()}.jpg")
        await self.client.download_profile_photo(user, file=photo_path)
        img = await convert_image_to_base64(photo_path)
        self._delete_file(photo_path, event)
        return img

    def _delete_file(self, file_path, event):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error deleting file: {e} - Event:\n {event}")

    def update_webhook_avatar(self, user_name, user_image_data_url, form_data_message):
        if self.last_user != user_name:
            if user_image_data_url:
                form_data_message.set_avatar(user_image_data_url)
            else:
                form_data_message.set_avatar_url(
                    "https://raw.githubusercontent.com/OniMock/.github/refs/heads/main/.resources/logo/fav_icon_logo.png")
        self.last_user = user_name

    async def _send_to_discord(self, form_data_message: Content, form_data, discord_service, event):
        try:
            await discord_service.send_message(form_data_message, form_data)
        except Exception as e:
            logger.error(f"Error sending message to discord: {e} - Event:\n{event}")

    async def _handle_reply(self, form_data_message, embed, event):
        original_message = await event.get_reply_message()
        if original_message and original_message.from_id and original_message.from_id.user_id:
            original_user = await original_message.get_sender()
            original_user_name = get_username(original_user)
            original_message_text = original_message.message

            if original_message.file:
                original_message_text += f"\n*{original_message.file.mime_type}*"

            if original_message_text:
                embed.add_field(original_user_name, original_message_text, False)
                embed.set_footer("Powered by Onimock")
                form_data_message.add_embed(embed)

    def _open_file_safely(self, files, document_path, event):
        try:
            files['file'] = open(document_path, 'rb')
        except Exception as e:
            logger.error(f"Error opening file: {e} - Event:\n{event}")

    def _close_file_safely(self, files, document_path, event):
        if 'file' in files:
            try:
                files['file'].close()
            except Exception as e:
                logger.error(f"Error closing file {document_path}: {e}")
            finally:
                self._delete_file(document_path, event)

