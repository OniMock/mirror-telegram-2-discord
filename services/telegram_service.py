import os
import logging
from telethon import TelegramClient, events
from telethon.errors import ChannelInvalidError, ChannelForumMissingError
from telethon.tl.functions.channels import JoinChannelRequest, GetForumTopicsByIDRequest, GetForumTopicsRequest
from telethon.tl.types import MessageMediaPoll, ForumTopic, Channel, User
from config import *
from models.identifier import Identifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramService:
    """
    Handles Telegram-related tasks such as authentication, group and subgroup retrieval,
    and message mirroring to Discord.

    Attributes:
        client: The Telethon client for interacting with Telegram.
        media_processor: Responsible for processing and storing media files.
        message_handler: Handles message formatting and sending to Discord.
    """

    def __init__(self, api_id, api_hash, media_processor, message_handler):
        self.client = TelegramClient(SESSION_NAME, api_id, api_hash)
        self.media_processor = media_processor
        self.message_handler = message_handler

    async def authenticate(self):
        """Authenticates the user with Telegram, prompting for code if required."""
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self._perform_authentication()

    async def _perform_authentication(self):
        """Handles two-factor authentication by requesting and verifying a code."""
        phone_number = input("Enter your phone number for authentication: ")
        await self.client.send_code_request(phone_number)
        code = input("Enter the code: ")
        await self.client.sign_in(phone_number, code)

    async def list_groups(self):
        """Lists all accessible Telegram channel groups."""
        groups = []
        async for dialog in self.client.iter_dialogs():
            if dialog.is_channel:
                groups.append(dialog)
        return groups

    async def get_group(self, group: Identifier):
        """
        Retrieves a specific group or joins one if an invitation link is provided.

        Args:
            group: An Identifier object representing group details.
        """
        try:
            if group.prop == 'link_invitation':
                join_channel = await self.client(JoinChannelRequest(group.group_id))
                return join_channel.chats[0]
            return await self.client.get_entity(group.group_id)
        except Exception as e:
            logger.error(f"Error fetching entity group {group.prop}: {e}")
            return None

    async def subgroup_name(self, group, subgroup_id):
        """
        Retrieves the name of a subgroup based on its ID.

        Args:
            group: The main group entity.
            subgroup_id: ID of the subgroup.
        """
        subgroup = await self.client(GetForumTopicsByIDRequest(
            channel=group,
            topics=[subgroup_id]
        ))
        return subgroup.topics[0].title if isinstance(subgroup.topics[0], ForumTopic) else None

    async def subgroups_topics(self, group):
        """
        Retrieves topics within a group, handling errors if the group is invalid or lacks forums.

        Args:
            group: Telegram group entity (e.g., Channel or User).
        """
        if isinstance(group, User):
            return None
        else:
            try:
                subgroups = await self.client(GetForumTopicsRequest(
                    channel=group,
                    offset_date=None,
                    offset_id=0,
                    offset_topic=0,
                    limit=100
                ))
                return subgroups.topics
            except (ChannelInvalidError, ChannelForumMissingError):
                return None

    async def get_entity_group(self, group):
        """Fetches a group entity given its identifier or link."""
        try:
            return await self.client.get_entity(group)
        except Exception as e:
            logger.error(f"Error fetching entity group: {e}")
            return None

    async def mirror_group_messages(self, group_id, discord_service, message_id=None):
        """
        Starts mirroring messages from a specified group to Discord, with an option to
        filter messages by reply threads.

        Args:
            group_id: ID of the group to mirror.
            discord_service: Service handling the delivery of messages to Discord.
            message_id: ID of a message to filter mirroring by replies (optional).
        """
        await self._ensure_save_directory_exists()
        async with (self.client):
            @self.client.on(events.NewMessage(chats=group_id))
            async def handler(event):
                if not isinstance(event.message.media, MessageMediaPoll):
                    reply_to = getattr(event.message, 'reply_to', None)
                    reply_to_top_id = getattr(reply_to, 'reply_to_top_id', None)
                    reply_to_msg_id = getattr(reply_to, 'reply_to_msg_id', None)

                    if message_id and reply_to:
                        if reply_to_top_id == message_id or reply_to_msg_id == message_id:
                            await self.message_handler.handle_new_message(discord_service, self.client, event)
                    elif not reply_to or not message_id:
                        await self.message_handler.handle_new_message(discord_service, self.client, event)

            print(f"Mirroring messages from group {group_id}. Press Ctrl+C to stop.")
            await self.client.run_until_disconnected()

    async def _ensure_save_directory_exists(self):
        """Ensures the directory for saving media files exists."""
        os.makedirs(self.media_processor.save_folder, exist_ok=True)
