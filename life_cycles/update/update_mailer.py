from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup


class UpdateMailer:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_update_to_subscriber(self, chat_id: int, image_path: str, text: str, keyboard: InlineKeyboardMarkup):
        await self.bot.send_photo(
            chat_id=chat_id,
            photo=image_path,
            caption=text,
            reply_markup=keyboard
        )
