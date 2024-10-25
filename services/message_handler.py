import os

import aiohttp

from models.content import Content
from models.embed import Embed
from models.user import get_username


class MessageHandler:
    """
    Handles the processing of new messages, including text, media, and replies,
    and prepares them for sending to Discord via webhooks.

    Attributes:
        media_processor: Processes and saves media content from messages.
        user_service: Retrieves additional user information such as profile image.
    """

    def __init__(self, media_processor, user_service):
        self.media_processor = media_processor
        self.user_service = user_service

    async def handle_new_message(self, discord_service, client, event):
        """
        Processes and formats a new Telegram message for Discord, adding text, media,
        user profile image, and reply details.

        Args:
            discord_service: Service handling message sending to Discord.
            client: Telethon client for accessing Telegram message details.
            event: Telegram message event containing the message content and media.
        """
        message_text = event.message.message
        user = await event.get_sender() or event.chat
        user_name = get_username(user)

        document_path = None
        files = {}
        form_data = aiohttp.FormData()
        embed = Embed('*reply*:')

        user_image_data_url = await self.user_service.get_user_image_data(client, user, event)
        form_data_message = Content(user_name)

        if event.message.media:
            document_path = await self.media_processor.process_media(client, event)
        if message_text:
            form_data_message.set_content(message_text)
        if event.message.reply_to_msg_id:
            await self._handle_reply(form_data_message, embed, event)
        if document_path:
            files['file'] = self.media_processor.file_manager.open_file_safely(document_path, event)
            form_data.add_field('files', files['file'], filename=os.path.basename(document_path))

        discord_service.update_webhook_avatar(user_name, user_image_data_url, form_data_message)
        try:
            await discord_service.send_message(form_data_message, form_data)
        finally:
            self.media_processor.file_manager.close_file_safely(files, document_path, event)

    @staticmethod
    async def _handle_reply(form_data_message, embed, event):
        """
        Adds reply information to the message, including reply text, user, and media details.

        Args:
            form_data_message: Content object representing the primary message data.
            embed: Embed object for formatting the reply message in Discord.
            event: Telegram message event used to access the reply message.
        """
        reply_message = await event.get_reply_message()
        if reply_message:
            reply_user = await reply_message.get_sender() or event.chat
            reply_user_name = get_username(reply_user)
            reply_message_text = reply_message.message
            if reply_message.file:
                reply_message_text += f"\n*{reply_message.file.mime_type}*"
            if reply_message_text:
                embed.add_field(reply_user_name, reply_message_text, False)
                embed.set_footer("Powered by Onimock")
                form_data_message.add_embed(embed)
