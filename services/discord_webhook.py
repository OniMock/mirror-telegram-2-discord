import json

import aiohttp

from models.content import Content


class DiscordWebhook:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    async def send_message(self, form_data_message: Content, form_data):
        async with aiohttp.ClientSession() as session:
            form_data.add_field('payload_json', json.dumps(form_data_message.to_dict()))
            if form_data_message.avatar:
                await self.send_avatar(form_data_message.avatar_to_dict(), session)
            await self._send_message(form_data, session)

    async def _send_message(self, form_data, session):
        try:
            async with session.post(self.webhook_url, data=form_data) as response:
                await self._handle_response(response)
        except Exception as e:
            print(f'An error occurred: {str(e)}')
            return False


    async def send_avatar(self, payload, session):
        try:
            async with session.patch(self.webhook_url, json=payload) as response:
                if response.status in [204, 200]:
                    print('Avatar updated successfully.')
                    return True
                else:
                    response_text = await response.text()
                    print(f'Error updating avatar:{response.status} - {response_text}')
                    return False
        except Exception as e:
            print(f'An error occurred while updating the avatar: {str(e)}')
            return False

    async def _handle_response(self,response):
        if response.status in [204, 200]:
            print('message sent successfully.')
            return True
        else:
            response_text = await response.text()
            print(f'Error sending message: {response.status} - {response_text}')
            return False



