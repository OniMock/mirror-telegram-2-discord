import os
import logging
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPoll
from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self, api_id, api_hash, media_processor, message_handler):
        self.client = TelegramClient(SESSION_NAME, api_id, api_hash)
        self.media_processor = media_processor
        self.message_handler = message_handler

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
        async for dialog in self.client.iter_dialogs():
            if dialog.is_channel:
                groups.append(dialog)
        return groups

    async def get_entity_group(self, group):
        try:
            group_entity = await self.client.get_entity(group)
            return group_entity
        except Exception as e:
            logger.error(f"Error fetching entity group: {e}")
            return None

    async def mirror_group_messages(self, group_id, discord_service):
        await self._ensure_save_directory_exists()
        async with self.client:
            @self.client.on(events.NewMessage(chats=group_id))
            async def handler(event):
                if not isinstance(event.message.media, MessageMediaPoll):
                    await self.message_handler.handle_new_message(discord_service, self.client, event)

            print(f"Mirroring messages from group {group_id}. Press Ctrl+C to stop.")
            await self.client.run_until_disconnected()

    async def _ensure_save_directory_exists(self):
        os.makedirs(self.media_processor.save_folder, exist_ok=True)
