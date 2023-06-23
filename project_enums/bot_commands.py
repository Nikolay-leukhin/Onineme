from enum import Enum


class BotCommands(Enum):
    start = {'name': 'start', 'description': 'начать'}
    help = {'name': 'help', 'description': 'доп инфа'}
    get_subs = {'name': 'mysubs', 'description': 'мои подписки'}
    choose_sub = {'name': 'choose', 'description': 'выбрать аниме'}
    search = {'name': 'search', 'description': 'икать аниме'}
