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
        """
        Updates the avatar of the webhook message based on the user's name and image data.

        If the user name has changed since the last update, it sets the avatar to the user's image URL
        or a default image if no user image is provided.

        Args:
            user_name (str): The name of the user whose avatar is to be updated.
            user_image_data_url (str): The data URL of the user's image.
            form_data_message: An object representing the message to be sent to the webhook,
                               which should have methods for setting the avatar.
        """
        if self.last_user != user_name:
            if user_image_data_url:
                form_data_message.set_avatar(user_image_data_url)
            else:
                form_data_message.set_avatar_url(
                    "https://raw.githubusercontent.com/OniMock/.github/refs/heads/main/.resources/logo/fav_icon_logo.png")
        self.last_user = user_name

    async def send_message(self, form_data_message: Content, form_data):
        """
        Sends a webhook message asynchronously with optional avatar data.

        This method constructs a session to send the message, adding the message
        payload and handling avatar data if provided.

        Args:
            form_data_message (Content): The message content, converted to a JSON payload.
            form_data: Form data object containing additional data for the webhook.
        """
        async with aiohttp.ClientSession() as session:
            form_data.add_field('payload_json', json.dumps(form_data_message.to_dict()))
            if form_data_message.avatar:
                await self._send_avatar(form_data_message.avatar_to_dict(), session)
            await self._send_message(form_data, session)

    async def _send_message(self, form_data, session):
        """
        Sends the prepared form data to the specified webhook URL.

        Tries to post the form data to the webhook URL, handling any exceptions
        that occur and logging errors if the request fails.

        Args:
            form_data: The data payload to send in the request.
            session: The aiohttp session used for sending the request.

        Returns:
            False if an exception occurs; otherwise, response handling proceeds.
        """
        try:
            async with session.post(self.webhook_url, data=form_data) as response:
                await self._handle_response(response)
        except Exception as e:
            logger.error(f'An error occurred: {str(e)} - Data:\n {form_data}')
            return False

    async def _send_avatar(self, payload, session):
        """
        Updates the webhook avatar by sending a PATCH request with avatar data.

        Attempts to update the avatar with the provided payload, logging the outcome
        based on response status and handling any exceptions.

        Args:
            payload (dict): JSON payload containing the avatar data.
            session: The aiohttp session used for sending the request.

        Returns:
            True if the avatar update is successful (status 200 or 204), False otherwise.
        """
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
        """
        Handles the response status for a webhook message request.

        Checks if the response indicates a successful request (status 200 or 204),
        logging success or logging an error message with the status and response
        content if unsuccessful.

        Args:
            response: The aiohttp response object from the message request.

        Returns:
            True if the response status is 200 or 204, indicating success; False otherwise.
        """
        if response.status in [204, 200]:
            logger.info('message sent successfully.')
            return True
        else:
            response_text = await response.text()
            logger.error(f'Error sending message: {response.status} - {response_text}')
            return False
