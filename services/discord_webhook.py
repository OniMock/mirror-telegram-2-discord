import aiohttp

class DiscordWebhook:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    async def send_message(self, payload):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as response:
                return response.status == 204  # HTTP status code for No Content
