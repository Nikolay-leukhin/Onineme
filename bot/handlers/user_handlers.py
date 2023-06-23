from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, StateFilter

from config_data.config import load_config
from data.database.database import DataBase
from data.schemas.user_schema import UserSchema
from bot.keyboards.choose_keys import create_pagination_key
from bot.keyboards.my_subscribe_key import create_my_subscribes_key
from bot.keyboards.subscribe_key import subscribe_keyboard
from bot.lexicon.lexicon import lexicon
from bot.logic.fsm import FSMSearch, FSMChoose, FSMShowSubs
from project_enums.bot_commands import BotCommands
from Levenshtein import ratio

router: Router = Router()
database: DataBase = DataBase(load_config().db)


@router.message(CommandStart())
async def process_start_command(msg: Message):
    chat_id: int = msg.chat.id
    name: str = msg.from_user.username

    if not database.is_user_exist(chat_id):
        user_model: UserSchema = UserSchema(
            chat_id=chat_id,
            username=name
        )
        database.register_user(user_model)

    await msg.answer(lexicon[BotCommands.start])


@router.message(Command(commands='help'))
async def process_start_command(msg: Message):
    await msg.answer(lexicon[BotCommands.help])


@router.message(Command(commands='mysubs'))
async def process_get_user_subscriptions(msg: Message, state: FSMContext):
    await state.set_state(FSMShowSubs.show_subscribes)

    chat_id: int = msg.chat.id
    subs = database.select_user_subscriptions(chat_id)
    await state.update_data(my_subs=subs)

    await msg.answer(text=lexicon[BotCommands.get_subs], reply_markup=create_my_subscribes_key(subs))


@router.message(Command(commands='choose'))
async def process_start_command(msg: Message, state: FSMContext):
    anime_list = database.select_all_not_ended_animes()
    if not anime_list:
        await msg.answer("Пока нет анимешек в онгоинге")
        return

    await state.set_state(FSMChoose.look_state)
    await state.update_data(anime_list=anime_list, page=0)

    anime_item = anime_list[0]
    text = create_poster_text(anime_item.name, anime_item.scenes_went, anime_item.scenes_total)
    await msg.answer_photo(
        photo=anime_item.image_path,
        caption=text,
        reply_markup=create_pagination_key(0, len(anime_list))
    )


@router.message(Command(commands='search'))
async def process_search_anime(msg: Message, state: FSMContext):
    await msg.answer(lexicon[BotCommands.search])
    await state.set_state(FSMSearch.fill_name)


@router.message(StateFilter(FSMSearch.fill_name))
async def process_search_anime_response(msg: Message, state: FSMContext):
    anime_name = msg.text.upper()

    anime_list = database.select_all_not_ended_animes()
    anime_db_item = [item for item in anime_list if ratio(item.name, anime_name) > 0.5]

    if anime_db_item.__len__() == 0:
        await msg.answer(text=lexicon['failure_search'])
        return

    item = anime_db_item[0]
    photo = item.image_path
    text = create_poster_text(name=item.name, scenes_went=item.scenes_went, scenes_total=item.scenes_total)

    await state.set_state(FSMSearch.handle_anime)
    await state.update_data(anime=item)
    await msg.answer_photo(caption=text, photo=photo, reply_markup=subscribe_keyboard(item))


def create_poster_text(name, scenes_went, scenes_total):
    text = f"🥀{name}🥀\n\nЭпизоды 🔥 {scenes_went} / {scenes_total if scenes_total is not None  else '🤷‍♂'}"
    return text


@router.message()
async def get_state(msg: Message, state: FSMContext):
    print(await state.get_state())
