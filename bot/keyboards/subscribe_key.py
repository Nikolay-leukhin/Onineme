from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_sub_button():
    sub_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='Подписаться',
        callback_data='sub',
    )
    return sub_btn


def create_cancel_btn(cb_data: str):
    cancel_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='Стоп',
        callback_data=cb_data
    )
    return cancel_btn


def create_watch_key(link) -> InlineKeyboardButton:
    watch_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='Смотреть',
        callback_data='watch',
        url=link
    )
    return watch_btn


def subscribe_keyboard(anime):
    sub_btn = create_sub_button()

    continue_btn: InlineKeyboardButton = InlineKeyboardButton(
        text="Искать дальше",
        callback_data='search'
    )

    cancel_btn = create_cancel_btn('cancel')
    watch_btn: InlineKeyboardButton = create_watch_key(anime.link)

    sub_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [sub_btn, watch_btn],
            [continue_btn, cancel_btn]
        ]
    )

    return sub_keyboard
