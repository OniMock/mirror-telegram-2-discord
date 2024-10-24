from config import DISCORD_WEBHOOK_URL
import os
from dotenv import load_dotenv
import asyncio

from models.identifier import Identifier
from services.discord_service import DiscordService
from services.media_processor import MediaProcessor
from services.message_handler import MessageHandler
from services.telegram_service import TelegramService
from services.user_service import UserService
from utils.check_string import CheckString
from utils.file_manager import FileManager
from utils.user_interface import UserInterface

load_dotenv()

telegram_api_id = os.getenv('TELEGRAM_API_ID')
telegram_api_hash = os.getenv('TELEGRAM_API_HASH')


async def main():
    discord_service = DiscordService(DISCORD_WEBHOOK_URL)
    file_manager = FileManager()
    media_processor = MediaProcessor(file_manager)
    user_service = UserService(file_manager)
    message_handler = MessageHandler(media_processor, user_service)
    telegram_service = TelegramService(int(telegram_api_id), telegram_api_hash, media_processor,
                                       message_handler)
    user_interface = UserInterface()
    await telegram_service.authenticate()

    while True:
        user_interface.display_menu()
        choice = user_interface.get_user_choice()
        if choice == '1':
            await handle_group_selection(telegram_service, user_interface, discord_service)
        elif choice == '2':
            await handle_group_mirroring(telegram_service, user_interface, discord_service)
        elif choice == '0':
            user_interface.exit()
            break
        else:
            print("Invalid choice, please try again.")


async def handle_group_selection(telegram_service, user_interface, discord_service):
    task = asyncio.create_task(telegram_service.list_groups())
    await show_loading_indicator(task)
    groups = await task
    user_interface.display_groups(groups)
    selected_index = user_interface.get_group_selection()
    print("\n" + "=" * 50 + "\n")

    if 0 <= selected_index < len(groups):
        group = groups[selected_index]
        sub_groups = await telegram_service.subgroups_topics(group)
        await start_mirroring_group(group, telegram_service, user_interface, discord_service,
                                    sub_groups=sub_groups)
    else:
        print("Invalid selection, please try again.")


async def handle_group_mirroring(telegram_service, user_interface, discord_service):
    group_choice: Identifier = CheckString.check_string_group(user_interface.get_group())
    group = await telegram_service.get_group(group_choice)
    await start_mirroring_group(group, telegram_service, user_interface, discord_service, group_choice=group_choice)


async def start_mirroring_group(group, telegram_service, user_interface, discord_service, sub_groups=None, group_choice=None):
    subgroup_name = None
    sub_group_id = None
    if group_choice and group_choice.subgroup_id:
        subgroup_name = await telegram_service.subgroup_name(group, group_choice.subgroup_id)
        if not subgroup_name:
            print(f"Subgroup informed does not exist for the group: {group.title}")
            return user_interface.exit()
        sub_group_id = group_choice.subgroup_id
    elif sub_groups:
        user_interface.display_subgroups(sub_groups)
        selected_index = user_interface.get_subgroup_selection()
        if selected_index == 0:
            pass
        elif 1 <= selected_index < len(sub_groups):
            selected_group = sub_groups[selected_index - 1]
            subgroup_name = selected_group.title
            sub_group_id = int(selected_group.id)
        else:
            print("Invalid selection, please try again.")
            return user_interface.exit()

    group_title = group.title if hasattr(group, 'title') else group.first_name
    group_username = group.username if hasattr(group, 'username') else "Without username"
    subgroup_name_display = f"\nSubgroup Name: {subgroup_name}" if subgroup_name else ""
    print("\n" + "=" * 50 + "\n")
    print(f"Starting mirroring of group:\nName:{group_title}\nUserName:{group_username}\nId:{group.id}{subgroup_name_display}")
    print("\n" + "=" * 50 + "\n")
    await telegram_service.mirror_group_messages(int(group.id), discord_service, sub_group_id)



async def show_loading_indicator(task):
    loading_symbols = ['.     ◐', '..    ◓', '...   ◑', '....  ◒', '...   ◐', '..    ◓', '.     ◑', '      ◒']
    idx = 0
    while not task.done():
        print(f"\rLoading groups{loading_symbols[idx % len(loading_symbols)]}", end="")
        idx += 1
        await asyncio.sleep(0.3)
    print("\r" + "\n", end="\n")


if __name__ == "__main__":
    asyncio.run(main())
