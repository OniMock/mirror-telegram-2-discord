from telethon import TelegramClient, events
from telethon.tl.types import User
from models.content import Content


class TelegramService:
    def __init__(self, api_id, api_hash, session_name):
        self.client = TelegramClient(session_name, api_id, api_hash)

    async def authenticate(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            phone_number = input("Enter your phone number for authentication: ")
            await self.client.send_code_request(phone_number)
            code = input("Enter the code: ")
            await self.client.sign_in(phone_number, code)

    async def list_groups(self):
        groups = []
        offset_id = 0
        last_offset_id = None
        max_iterations = 10
        iteration_count = 0

        while True:
            dialogs = await self.client.get_dialogs(offset_id=offset_id, limit=100)

            if not dialogs:
                break

            for dialog in dialogs:
                if dialog.is_group:
                    groups.append(dialog)

            last_message_id = dialogs[-1].message.id if dialogs[-1].message else None

            if last_message_id:
                offset_id = last_message_id
            else:
                break

            if offset_id == last_offset_id:
                break

            last_offset_id = offset_id
            iteration_count += 1

            if iteration_count >= max_iterations:
                break

        return groups

    async def mirror_group_messages(self, group_id, discord_service):
        async with self.client:
            @self.client.on(events.NewMessage(chats=group_id))
            async def handler(event):
                message_text = event.message.message
                user = await event.get_sender()

                if message_text and isinstance(user, User):
                    user_name = user.username
                    user_photo = user.photo
                    payload = Content(user_name, message_text, user_photo)

                    try:
                        response = await discord_service.send_message(payload.format_payload())
                        if response is None:
                            print("send_message return None.")
                    except Exception as e:
                        print(f"Error to send message to discord: {e}")

            print(f"Mirroring messages from group {group_id}. Press Ctrl+C to stop.")
            await self.client.run_until_disconnected()
