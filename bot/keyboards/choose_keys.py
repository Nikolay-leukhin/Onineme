from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.subscribe_key import create_cancel_btn, create_sub_button


def create_pagination_key(cur_page, all_pages):
    next_anime: InlineKeyboardButton = InlineKeyboardButton(
        text='➡',
        callback_data='next_anime',
    )

    prev_anime: InlineKeyboardButton = InlineKeyboardButton(
        text='⬅',
        callback_data='prev_anime',
    )

    page_number: InlineKeyboardButton = InlineKeyboardButton(
        text=f'{cur_page} / {all_pages}',
        callback_data="pagination_data"
    )

    pagination_anime_list: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[
        [prev_anime, page_number, next_anime],
        [create_sub_button(), create_cancel_btn('cancel_show_anime_choose')]

    ])

    return pagination_anime_list
