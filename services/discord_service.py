import json
import logging

import aiohttp

from models.content import Content

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordService:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.last_user = None

    def update_webhook_avatar(self, user_name, user_image_data_url, form_data_message):
        if self.last_user != user_name:
            if user_image_data_url:
                form_data_message.set_avatar(user_image_data_url)
            else:
                form_data_message.set_avatar_url(
                    "https://raw.githubusercontent.com/OniMock/.github/refs/heads/main/.resources/logo/fav_icon_logo.png")
        self.last_user = user_name

    async def send_message(self, form_data_message: Content, form_data):
        async with aiohttp.ClientSession() as session:
            form_data.add_field('payload_json', json.dumps(form_data_message.to_dict()))
            if form_data_message.avatar:
                await self._send_avatar(form_data_message.avatar_to_dict(), session)
            await self._send_message(form_data, session)

    async def _send_message(self, form_data, session):
        try:
            async with session.post(self.webhook_url, data=form_data) as response:
                await self._handle_response(response)
        except Exception as e:
            logger.error(f'An error occurred: {str(e)} - Data:\n {form_data}')
            return False

    async def _send_avatar(self, payload, session):
        try:
            async with session.patch(self.webhook_url, json=payload) as response:
                if response.status in [204, 200]:
                    logger.info('Avatar updated successfully.')
                    return True
                else:
                    response_text = await response.text()
                    logger.info(f'Error updating avatar:{response.status} - {response_text}')
                    return False
        except Exception as e:
            logger.error(f'An error occurred while updating the avatar: {str(e)}')
            return False

    @staticmethod
    async def _handle_response(response):
        if response.status in [204, 200]:
            logger.info('message sent successfully.')
            return True
        else:
            response_text = await response.text()
            logger.error(f'Error sending message: {response.status} - {response_text}')
            return False
