from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_factories.anime_callback_data import AnimeCallbackData


def edit_my_subscribes_key(subs):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for btn in subs:
        kb_builder.row(
            InlineKeyboardButton(
                text=f"🗑 {str(btn.name)}",
                callback_data=AnimeCallbackData(
                    id=btn.id,
                ).pack(),
            )
        )
    kb_builder.row(
        InlineKeyboardButton(
            text='Отмена 🚫',
            callback_data='cansel_deleting'
        )
    )

    return kb_builder.as_markup()


def create_my_subscribes_key(subs):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for btn in subs:
        kb_builder.row(
            InlineKeyboardButton(
                text=str(btn.name),
                callback_data=f"anime_data"
            )
        )
    kb_builder.row(
        InlineKeyboardButton(
            text='Edit 📝',
            callback_data='edit'
        ),
        InlineKeyboardButton(
            text='Отмена 🚫',
            callback_data='cansel_show_anime_subs'
        )
    )

    return kb_builder.as_markup()
