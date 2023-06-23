from aiogram.types import BotCommand

from project_enums.bot_commands import BotCommands

menu_commands: list[BotCommand] = [
    BotCommand(
        command=f"/{item.value['name']}",
        description=item.value['description']
    ) for item in BotCommands
]
