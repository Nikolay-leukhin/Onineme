from aiogram.filters.callback_data import CallbackData


class AnimeCallbackData(CallbackData, prefix='anime'):
    id: int
