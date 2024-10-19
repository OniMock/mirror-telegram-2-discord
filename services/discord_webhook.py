import aiohttp

class DiscordWebhook:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    async def send_message2(self, payload, image):
        async with aiohttp.ClientSession() as session:
            check = await self.send_avatar(image, session)
            await self.send_message(payload, session)
            return check

    async def send_message(self, payload, session):
        try:
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status in [204, 200]:
                    print('message sent successfully.')
                    return True
                else:
                    response_text = await response.text()
                    print(f'Error sending message: {response.status} - {response_text}')
                    return False

        except Exception as e:
            print(f'An error occurred: {str(e)}')
            return False


    async def send_avatar(self, image, session):
        try:
            async with session.patch(self.webhook_url, json={'avatar': image}) as response:
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



