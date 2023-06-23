from aiogram.fsm.state import StatesGroup, State


class FSMShowSubs(StatesGroup):
    show_subscribes = State()


class FSMSearch(StatesGroup):
    fill_name = State()
    handle_anime = State()


class FSMChoose(StatesGroup):
    look_state = State()
