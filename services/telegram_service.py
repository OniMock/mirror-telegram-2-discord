import mimetypes
import os
import aiohttp
import logging
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaPoll, MessageMediaDocument
from models.content import Content
from models.embed import Embed
from models.user import get_username
from utils.image_to_base64 import convert_image_to_base64
from utils.file_manager import FileManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self, api_id, api_hash, session_name):
        self.save_folder = "profile_files/"
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.last_user = None
        self.file_manager = FileManager(self.save_folder)

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
        async for dialog in self.client.iter_dialogs():
            if dialog.is_channel:
                groups.append(dialog)
                seen_ids.add(dialog.id)
        return groups

    async def get_entity_group(self, group):
        try:
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
            files['file'] = self.file_manager.open_file_safely(document_path, event)
        if files:
            form_data.add_field('files', files['file'], filename=document_path.split('/')[-1])

        self.update_webhook_avatar(user_name, user_image_data_url, form_data_message)
        try:
            await self._send_to_discord(form_data_message, form_data, discord_service, event)
        finally:
            self.file_manager.close_file_safely(files, document_path, event)

    async def _get_user_image_data(self, user, event):
        photo_path = self.file_manager.generate_filename('img', '.jpg')
        await self.client.download_profile_photo(user, file=photo_path)
        img = await convert_image_to_base64(photo_path)
        self.file_manager.delete_file(photo_path, event)
        return img

    async def _get_user_document(self, event):
        if isinstance(event.message.media, MessageMediaDocument):
            mime_type = event.message.media.document.mime_type
        elif isinstance(event.message.media, MessageMediaPhoto):
            mime_type = 'image/jpeg'
        else:
            logger.warning(f"Unsupported media type: {type(event.message.media).__name__}")
            return None
        extension = mimetypes.guess_extension(mime_type) or '.bin'
        media_path = self.file_manager.generate_filename(f"{'doc_img' if isinstance(event.message.media, MessageMediaPhoto) else 'doc_file'}_", extension)
        await self.client.download_media(event.message, file=media_path)
        return media_path

    def update_webhook_avatar(self, user_name, user_image_data_url, form_data_message):
        if self.last_user != user_name:
            form_data_message.set_avatar(user_image_data_url or "https://raw.githubusercontent.com/OniMock/.github/refs/heads/main/.resources/logo/fav_icon_logo.png")
        self.last_user = user_name

    async def _send_to_discord(self, form_data_message, form_data, discord_service, event):
        try:
            await discord_service.send_message(form_data_message, form_data)
        except Exception as e:
            logger.error(f"Error sending message to Discord: {e} - Event:\n{event}")

    async def _handle_reply(self, form_data_message, embed, event):
        reply_message = await event.get_reply_message()
        if reply_message and reply_message.from_id:
            reply_user = await reply_message.get_sender() or event.chat
            reply_user_name = get_username(reply_user)
            reply_message_text = reply_message.message
            if reply_message.file:
                reply_message_text += f"\n*{reply_message.file.mime_type}*"
            if reply_message_text:
                embed.add_field(reply_user_name, reply_message_text, False)
                embed.set_footer("Powered by Onimock")
                form_data_message.add_embed(embed)
