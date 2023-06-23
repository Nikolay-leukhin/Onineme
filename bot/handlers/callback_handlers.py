from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto

from bot.callback_factories.anime_callback_data import AnimeCallbackData
from config_data.config import load_config
from data.database.database import DataBase
from data.schemas.anime_subscription_schema import AnimeSubscriptionSchema
from bot.handlers.user_handlers import create_poster_text
from bot.keyboards.choose_keys import create_pagination_key
from bot.keyboards.my_subscribe_key import edit_my_subscribes_key, create_my_subscribes_key
from bot.lexicon.lexicon import lexicon
from bot.logic.fsm import FSMSearch, FSMChoose
from project_enums.bot_commands import BotCommands
from project_enums.status import Status

router: Router = Router()
database: DataBase = DataBase(load_config().db)


@router.callback_query(Text(text='sub'))
async def process_subscribe_btn_pressed(cb: CallbackQuery, state: FSMContext):
    chat_id = cb.message.chat.id
    anime = await state.get_data()
    current_state = await state.get_state()

    anime_id = None
    if current_state == FSMSearch.handle_anime:
        anime_id = anime['anime'].id
    elif current_state == FSMChoose.look_state:
        anime_id = anime['anime_list'][anime['page']].id
    else:
        await cb.answer(lexicon['failure_subscribe_server'])
        return

    subscription: AnimeSubscriptionSchema = AnimeSubscriptionSchema(
        user_id=chat_id,
        title_id=anime_id
    )

    result_subscription = database.register_subscription(subscription)
    if result_subscription is Status.success:
        await cb.answer(lexicon['success_subscribe'])
    else:
        await cb.answer(lexicon['failure_subscribe'])


@router.callback_query(Text(text='search'))
async def process_button_search_more_pressed(cb: CallbackQuery, state: FSMContext):
    await state.set_state(FSMSearch.fill_name)
    await cb.message.answer(lexicon[BotCommands.search])
    await cb.answer()


@router.callback_query(Text(text='cancel'))
async def process_button_search_more_pressed(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.answer(lexicon['stop_searching'])
    await cb.answer()


@router.callback_query(Text(text='cancel_show_anime_choose'))
async def process_button_search_more_pressed(cb: CallbackQuery, state: FSMContext):
    if await state.get_state() == FSMChoose.look_state:
        await state.clear()
        await cb.message.answer(lexicon['stop_searching'])
    await cb.answer()


@router.callback_query(Text(text='edit'))
async def process_editing_my_anime_list(cb: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    my_subs = state_data['my_subs']
    await cb.message.edit_reply_markup(
        reply_markup=edit_my_subscribes_key(my_subs)
    )


@router.callback_query(AnimeCallbackData.filter())
async def process_deleting_anime(cb: CallbackQuery, callback_data: AnimeCallbackData, state: FSMContext):
    state_data = await state.get_data()
    my_subs = state_data['my_subs']

    database.delete_subscription(
        chat_id=cb.message.chat.id,
        anime_id=callback_data.id
    )

    for note in my_subs:
        if note.id == callback_data.id:
            my_subs.remove(note)
            break

    await cb.message.edit_reply_markup(
        reply_markup=edit_my_subscribes_key(my_subs)
    )
    await cb.answer()


@router.callback_query(Text(text='cansel_deleting'))
async def process_cancel_anime_deleting(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    my_subs = data['my_subs']
    await cb.message.edit_reply_markup(
        reply_markup=create_my_subscribes_key(my_subs)
    )
    await cb.answer()


@router.callback_query(Text(text='cansel_show_anime_subs'))
async def process_cancel_showing_my_subs(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text(lexicon['subs_close'])
    await cb.answer()


@router.callback_query(Text(text=['next_anime', 'prev_anime']))
async def process_next_anime_page(cb: CallbackQuery, state: FSMContext):
    if await state.get_state() == FSMChoose.look_state:
        state_data = await state.get_data()
        anime_list = state_data['anime_list']
        cur_page = state_data['page']
        if cb.data == 'next_anime':
            next_page = cur_page + 1 if cur_page + 1 != len(state_data['anime_list']) else 0
        else:
            next_page = cur_page - 1 if cur_page > 0 else len(anime_list) - 1

        await state.update_data(page=next_page)

        page = anime_list[next_page]
        name = create_poster_text(page.name, page.scenes_went, page.scenes_total)
        image = InputMediaPhoto(media=page.image_path, caption=name)
        await cb.message.edit_media(
            media=image,
            reply_markup=create_pagination_key(next_page, len(anime_list))
        )
    await cb.answer()


@router.callback_query(Text(text='pagination_data'))
async def process_pagination_info_pressed(cb: CallbackQuery):
    await cb.answer("📖")


