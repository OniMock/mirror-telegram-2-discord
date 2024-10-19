
from config import SESSION_NAME, DISCORD_WEBHOOK_URL
import os
from dotenv import load_dotenv
import asyncio
from services.discord_webhook import DiscordWebhook
from services.telegram_service import TelegramService
from utils.user_interface import UserInterface

load_dotenv()

telegram_api_id = os.getenv('TELEGRAM_API_ID')
telegram_api_hash = os.getenv('TELEGRAM_API_HASH')

async def main():

    discord_service = DiscordWebhook(DISCORD_WEBHOOK_URL)
    telegram_service = TelegramService(int(telegram_api_id), telegram_api_hash, SESSION_NAME)
    user_interface = UserInterface()
    await telegram_service.authenticate()

    while True:
        user_interface.display_menu()
        choice = user_interface.get_user_choice()

        if choice == '1':
            groups = await telegram_service.list_groups()
            user_interface.display_groups(groups)
            selected_index = user_interface.get_group_selection()

            if 0 <= selected_index < len(groups):
                selected_group = groups[selected_index]
                print(f"Starting mirroring of group: {selected_group.name} (ID: {selected_group.id})")
                await telegram_service.mirror_group_messages(selected_group.id, discord_service)
            else:
                print("Invalid selection, please try again.")
        elif choice == '2':
            group_at = user_interface.get_group_by_at()
            group_id = await telegram_service.get_group_by_at(group_at)
            print(f"Starting mirroring of group with username at(@): {group_id.channel_id}")
            await telegram_service.mirror_group_messages(int(group_id.channel_id), discord_service)

        elif choice == '3':
            group_id = user_interface.get_group_id()
            print(f"Starting mirroring of group with ID: {group_id}")
            await telegram_service.mirror_group_messages(int(group_id), discord_service)

        elif choice == '0':
            user_interface.exit()
            break

        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    asyncio.run(main())

