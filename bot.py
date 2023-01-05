import logging
import asyncio

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode

from credlib import API_TOKEN
import markup as nav
from db.sql import Database
from forms import FormSub, FormEdit, FormUnSub, FormSendReq

from pprint import pprint


# Настройка ведения журнала
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)

# Значение представляет собой большой двоичный объект данных, сохраненный точно в том виде, в каком он был введен.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация БД
db = Database("db/sqlite3.db")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """
    Старт бота
    """
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
        await bot.send_message(message.from_user.id, "Стартуем! 🚀", reply_markup=nav.menu)
    else:
        await bot.send_message(message.from_user.id, "Бот уже был запущен 🤖", reply_markup=nav.menu)


# ************************************************************* START /menu
@dp.message_handler(commands=['menu'])
async def menu(message: types.Message):
    if message.message.chat.type == 'private':
        message_data = message.data
        db_list = db.get_user(message.from_user.id)[0]
        if message_data == 'btnProfile':
            if db_list[3]:
                text = f'Ваши учётные данные:\n\nid: {db_list[1]}\nnickname: {db_list[2]}\ncreate date: {db_list[4]}'
                await bot.send_message(message.from_user.id, text, reply_markup=nav.artist_profile_menu)
            else:
                text = f'Ваши учётные данные:\n\nid: {db_list[1]}\ncreate date: {db_list[4]}'
                await bot.send_message(message.from_user.id, text, reply_markup=nav.user_profile_menu)
        elif message_data == 'btnRequests':
            if db_list[3]:
                await bot.send_message(message.from_user.id, 'Requests', reply_markup=nav.artist_requests_menu)
            else:
                await bot.send_message(message.from_user.id, 'Requests', reply_markup=nav.user_requests_menu)
# ************************************************************* END /menu


# ************************************************************* START /button_handler_sub
@dp.callback_query_handler(text_contains='btnConf')
async def button_handler_sub(call: types.CallbackQuery):
    """
    Обрабатывает кнопку `Subscribe`.
        С её помощью пользователь может стать художником и брать заказы других пользователей.

    Здесь точка входа в разговор
    """
    await asyncio.sleep(0.5)
    await FormSub.artist.set()

    message_dict = call.message
    if message_dict.chat.type == 'private':
        if db.user_type(call.from_user.id)[0][0]:
            await bot.send_message(call.from_user.id, 'Вы уже художник.', reply_markup=nav.artist_profile_menu)
        else:
            await bot.send_message(call.from_user.id, 'Вы уверены, что хотите стать художником?',
                                   reply_markup=nav.conf_menu)


@dp.callback_query_handler(lambda call: call.data not in ["btnConfYes", "btnConfNo"],
                           state=FormSub.artist, text_contains='btnConf')
async def sub_step_1(call: types.CallbackQuery):
    """
    Проверяем ответ. Должен быть один из вариантов: Yes или No (внутренние названия ["btnConfYes", "btnConfNo"])
    """
    return await call.message.reply("Неверный ответ, варианты: `Yes`, `No`.", reply_markup=nav.conf_menu)


@dp.callback_query_handler(state=FormSub.artist)
async def sub_step_2(call: types.CallbackQuery, state: FSMContext):
    """
    Отрабатываем ответ
    """
    async with state.proxy() as data:
        data['artist'] = 1

    await FormSub.next()
    if call.data == 'btnConfNo':
        await call.message.reply("Подписка отменена.", reply_markup=nav.user_profile_menu)
        await state.finish()
    else:
        await call.message.reply("Введите никнейм")


@dp.message_handler(lambda message: True in [i in message.text for i in "{}[]:;]/|\.,<>!@#$%^&*"],
                    state=FormSub.nickname)
async def sub_step_3(message: types.Message):
    """
    Проверяем формат `nickname`
    """
    text = message.reply_markup.inline_keyboard[1][0].text
    if not isinstance(text, str) and not text[0].isdigit():
        return await message.reply("Неверный формат.")
    elif 3 > len(text) > 15:
        return await message.reply("Длинна `nickname` не должна превышать 14 символов, минимальное кол-во 4 символа.")
    return await message.reply("Недопустимые символы.")


@dp.message_handler(state=FormSub.nickname)
async def last_step(message: types.Message, state: FSMContext):
    """
    После всех необходимых проверок и ответов пользователя записываем полученные данные в БД и завершаем разговор
    """
    async with state.proxy() as data:
        text = message.text
        data['nickname'] = text

        # И отправить сообщение
        await bot.send_message(message.chat.id,
                               'Отлично! Теперь Вы художник и можете выполнять заказы от пользователей!',
                               reply_markup=nav.menu,
                               parse_mode=ParseMode.MARKDOWN)
        db.update_artist(data['artist'], message.from_user.id)
        db.update_nickname(data['nickname'], message.from_user.id)
        await asyncio.sleep(0.5)

        # Закончить разговор
        await state.finish()
# ************************************************************* END /button_handler_sub


# ************************************************************* START /button_handler_edit
@dp.callback_query_handler(text_contains='btnConf')
async def button_handler_edit(call: types.CallbackQuery):
    """
    Обрабатывает кнопку `Edit profile`.
    Меняет для художника его `nickname`

    Здесь точка входа в разговор
    """
    await asyncio.sleep(0.5)
    await FormEdit.nickname.set()

    message_dict = call.message
    if message_dict.chat.type == 'private':
        if db.user_type(call.from_user.id)[0][0]:
            await bot.send_message(call.from_user.id, 'Вы уверены, что хотите изменить `nickname`?',
                                   reply_markup=nav.conf_menu)


@dp.callback_query_handler(lambda call: call.data not in ["btnConfYes", "btnConfNo"],
                           state=FormEdit.nickname, text_contains='btnConf')
async def sub_step_1(call: types.CallbackQuery):
    """
    Проверяем ответ. Должен быть один из вариантов: Yes или No (внутренние названия ["btnConfYes", "btnConfNo"])
    """
    return await call.message.reply("Неверный ответ, варианты: `Yes`, `No`.", reply_markup=nav.conf_menu)


@dp.callback_query_handler(state=FormEdit.nickname)
async def sub_step_2(call: types.CallbackQuery, state: FSMContext):
    """
    Отрабатываем ответ `button_handler_edit` после предварительной проверки на `sub_step_1`
    """
    if call.data == 'btnConfNo':
        await call.message.reply("Редактирование профиля отменено.", reply_markup=nav.artist_profile_menu)
        await state.finish()
    else:
        await call.message.reply("Введите новый никнейм")


# Проверяем формат nickname
@dp.message_handler(lambda message: True in [i in message.text for i in "{}[]:;]/|\.,<>!@#$%^&*"],
                    state=FormEdit.nickname)
async def sub_step_3(message: types.Message):
    """
    Если введён неверный формат
    """
    text = message.reply_markup.inline_keyboard[1][0].text
    if not isinstance(text, str) and not text[0].isdigit():
        return await message.reply("Неверный формат.")
    elif 3 > len(text) > 15:
        return await message.reply("Длинна `nickname` не должна превышать 14 символов, минимальное кол-во 4 символа.")
    return await message.reply("Недопустимые символы.")


@dp.message_handler(state=FormEdit.nickname)
async def last_step(message: types.Message, state: FSMContext):
    """
    После всех необходимых проверок и ответов пользователя записываем полученные данные в БД и завершаем разговор
    """
    async with state.proxy() as data:
        text = message.text
        data['nickname'] = text

        # И отправить сообщение
        await bot.send_message(message.chat.id,
                               md.text(
                                   md.text(f'Отлично! `Nickname` изменён на: {data["nickname"]}'),
                                   sep='\n',
                               ),
                               reply_markup=nav.menu,
                               parse_mode=ParseMode.MARKDOWN)
        db.update_nickname(data['nickname'], message.from_user.id)
        await asyncio.sleep(0.5)

        # Закончить разговор
        await state.finish()
# ************************************************************* END /button_handler_edit


# ************************************************************* START /button_handler_unsub
@dp.callback_query_handler(text_contains='btnConf')
async def button_handler_unsub(call: types.CallbackQuery):
    """
    Обрабатывает кнопку `Unsubscribe`.
    Позволяет художнику отказаться роли художника и стать обычным пользователем

    Здесь точка входа в разговор
    """
    await asyncio.sleep(0.5)
    await FormUnSub.artist.set()

    message_dict = call.message
    if message_dict.chat.type == 'private':
        if db.user_type(call.from_user.id)[0][0]:
            await bot.send_message(call.from_user.id, 'Вы уверены, что хотите отменить подписку?',
                                   reply_markup=nav.conf_menu)


@dp.callback_query_handler(lambda call: call.data not in ["btnConfYes", "btnConfNo"],
                           state=FormUnSub.artist, text_contains='btnConf')
async def sub_step_1(call: types.CallbackQuery):
    """
    Проверяем ответ. Должен быть один из вариантов: Yes или No (внутренние названия ["btnConfYes", "btnConfNo"])
    """
    return await call.message.reply("Неверный ответ, варианты: `Yes`, `No`.", reply_markup=nav.conf_menu)


@dp.callback_query_handler(state=FormUnSub.artist)
async def sub_step_2(call: types.CallbackQuery, state: FSMContext):
    """
    Отрабатываем ответ `button_handler_unsub` после предварительной проверки на `sub_step_1`, затем записываем
        полученные данные в БД, при необходимости, и завершаем разговор
    """
    async with state.proxy() as data:
        data['artist'] = 0
        data['nickname'] = ''

    if call.data == 'btnConfNo':
        await call.message.reply("Отписка отменена.", reply_markup=nav.artist_profile_menu)
        await state.finish()
    else:
        await call.message.reply("Подписка отменена.", reply_markup=nav.user_profile_menu)
        db.update_artist(data['artist'], call.from_user.id)
        db.update_nickname(data['nickname'], call.from_user.id)
        await state.finish()
# ************************************************************* END /button_handler_unsub


# ************************************************************* START /send_request
@dp.callback_query_handler(text_contains='btnConf')
async def button_handler_send_request(call: types.CallbackQuery):
    """
    Обрабатывает кнопку `Send request`.
        С её помощью пользователь/художник может запрашивать у художников картину по описанию.

    Здесь точка входа в разговор
    """
    await asyncio.sleep(0.5)
    await FormSendReq.text.set()

    message_dict = call.message
    if message_dict.chat.type == 'private':
        if db.user_type(call.from_user.id)[0][0]:
            await bot.send_message(call.from_user.id,
                                   'Вы действительно хотите запросить у других художников картину?',
                                   reply_markup=nav.conf_menu)
        else:
            await bot.send_message(call.from_user.id,
                                   'Вы действительно хотите запросить у художников картину?',
                                   reply_markup=nav.conf_menu)


@dp.callback_query_handler(lambda call: call.data not in ["btnConfYes", "btnConfNo"],
                           state=FormSendReq.text, text_contains='btnConf')
async def sub_step_1(call: types.CallbackQuery):
    """
    Проверяем ответ. Должен быть один из вариантов: Yes или No (внутренние названия ["btnConfYes", "btnConfNo"])
    """
    return await call.message.reply("Неверный ответ, варианты: `Yes`, `No`.", reply_markup=nav.conf_menu)


@dp.callback_query_handler(state=FormSendReq.text)
async def sub_step_2(call: types.CallbackQuery, state: FSMContext):
    """
    Отрабатываем ответ `button_handler_send_request` после предварительной проверки на `sub_step_1`
    """
    if call.data == 'btnConfNo':
        if db.user_type(call.from_user.id)[0][0]:
            # ответ художнику
            await bot.send_message(call.from_user.id, 'Запрос картины отменён.', reply_markup=nav.artist_requests_menu)
        else:
            # ответ пользователю
            await bot.send_message(call.from_user.id, 'Запрос картины отменён.', reply_markup=nav.user_requests_menu)
        await state.finish()
    else:
        await call.message.reply("Введите описание картины")


@dp.message_handler(lambda message: 3 > len(message.text) > 15, state=FormSendReq.text)
async def sub_step_3(message: types.Message):
    """
    Если введён неверный формат
    """
    return await message.reply("Неверный формат. Введите текст от 3 до 15 символов.")


@dp.message_handler(state=FormSendReq.text)
async def last_step(message: types.Message, state: FSMContext):
    """
    После всех необходимых проверок и ответов пользователя записываем полученные данные в БД и завершаем разговор
    """
    async with state.proxy() as data:
        text = message.text
        data['text'] = text

        # И отправить сообщение
        bot_answer = f'Отлично! Ваш запрос отправлен художникам.'
        type_user = db.user_type(message.chat.id)[0][0]
        if type_user:
            await bot.send_message(message.chat.id, bot_answer, reply_markup=nav.artist_requests_menu,
                                   parse_mode=ParseMode.MARKDOWN)

            # отправляем всем художникам созданный пользователем/художником запрос на картину
            db_list = db.show_artists()
            bot_answer = f'От пользователя: {message.chat.id}\nОписания запроса: `{text}`'
            [await bot.send_message(i, bot_answer, reply_markup=nav.not_accepted_request) for i in db_list]
        else:
            await bot.send_message(message.chat.id, bot_answer, reply_markup=nav.user_requests_menu,
                                   parse_mode=ParseMode.MARKDOWN)

        db.add_request(data['text'], message.from_user.id)
        await asyncio.sleep(0.5)
        # Закончить разговор
        await state.finish()
# ************************************************************* END /send_request


# ************************************************************* START /show_requests
@dp.message_handler(commands=['requests'])
async def show_requests(message: types.Message):
    if message.message.chat.type == 'private':
        message_data = message.data
        if message_data == 'btnShowFreeRequests':
            quantity = 3

            # перебираем выгрузку с БД от `show_requests` и отсеиваем выполненные/закрытые запросы
            result = [i for i in db.show_requests() if i[3] != 'closed' and i[3] != 'completed'][-quantity:]

            if len(result):
                for i in range(len(result)):
                    text = f'id request: {result[i][0]}\n' \
                           f'user id: {result[i][1]}\n' \
                           f'text request: {result[i][2]}\n' \
                           f'date: {result[i][5]}'
                    if result[i][3] == 'not accepted':
                        await bot.send_message(message.from_user.id, text, reply_markup=nav.not_accepted_request)
                    if result[i][3] == 'accepted':
                        await bot.send_message(message.from_user.id, text, reply_markup=nav.accepted_request)
            else:
                await bot.send_message(message.from_user.id, 'Нет свободных запросов',
                                       reply_markup=nav.back_artist_requests)

        elif message_data == 'btnShowAcceptedRequests':
            quantity = 3

            # то же самое действие, что и выше в `if`
            db_list = db.show_accepted_request(message.from_user.id)
            result = [i for i in db_list if i[3] != 'closed' and i[3] != 'completed'][-quantity:]
            if len(result):
                for i in range(len(result)):
                    text = f'id request: {result[i][0]}\nuser id: {result[i][1]}\n' \
                           f'text request: {result[i][2]}\ndate: {result[i][5]}'
                    await bot.send_message(message.from_user.id, text, reply_markup=nav.accepted_request)
            else:
                await bot.send_message(message.from_user.id, 'Вы не приняли ни одного запроса',
                                       reply_markup=nav.back_artist_requests)

        elif message_data == 'btnShowMyRequests':
            # то же самое действие, что и выше в `if`
            db_list = db.show_my_requests(message.from_user.id)
            result = [i for i in db_list if i[3] != 'closed' and i[3] != 'completed']

            if len(result):
                for i in range(len(result)):
                    text = f'id request: {result[i][0]}\nuser id: {message.from_user.id}\ntext request: {result[i][2]}\n' \
                           f'status: {result[i][3]}\nupdate date: {result[i][4]}\ncreate date: {result[i][5]}'
                    await bot.send_message(message.from_user.id, text, reply_markup=nav.accepted_request)
            else:
                if db.get_user(message.from_user.id)[0][3]:
                    await bot.send_message(message.from_user.id, 'Нет открытых запросов',
                                           reply_markup=nav.back_artist_requests)
                else:
                    await bot.send_message(message.from_user.id, 'Нет открытых запросов',
                                           reply_markup=nav.back_user_requests)

# ************************************************************* END /show_requests


# ************************************************************* START /update_request
@dp.message_handler(commands=['requests'])
async def update_request(message: types.Message):
    if message.message.chat.type == 'private':
        message_data = message.data
        request_text = message.message.text[12:]

        user_id = message.message.chat.id
        request_id = request_text[:(request_text.find("u")) - 1]

        if message_data == 'btnAccept':
            text = 'Вы приняли в работу запрос пользователя'
            db.update_request(user_id, 'accepted', request_id)
            await bot.send_message(message.from_user.id, text, reply_markup=nav.accepted_request)
        elif message_data == 'btnClose':
            text = 'Вы закрыли запрос'
            db.update_request(user_id, 'closed', request_id)
            await bot.send_message(message.from_user.id, text, reply_markup=nav.artist_requests_menu)
        elif message_data == 'btnCompleted':
            text = 'Вы успешно завершили запрос'
            db.update_request(user_id, 'completed', request_id)
            await bot.send_message(message.from_user.id, text, reply_markup=nav.artist_requests_menu)
# ************************************************************* END /update_request


# ************************************************************* START /back
@dp.message_handler(commands=['back'])
async def back(message: types.Message):
    if message.message.chat.type == 'private':
        message_data = message.data
        if message_data == 'btnBack':
            await bot.send_message(message.from_user.id, 'Menu', reply_markup=nav.menu)
        elif message_data == 'btnBackUserRequests':
            await bot.send_message(message.from_user.id, 'Requests', reply_markup=nav.user_requests_menu)
        elif message_data == 'btnBackArtistRequests':
            await bot.send_message(message.from_user.id, 'Requests', reply_markup=nav.artist_requests_menu)
# ************************************************************* END /back


@dp.callback_query_handler(text_contains='btn')
async def btnIn_handler(call: types.CallbackQuery):
    """
    Обрабатывает основные кнопки и перенаправляет на необходимые функции
    """

    if call.data == 'btnProfile':
        await menu(call)
    elif call.data == 'btnRequests':
        await menu(call)
    elif call.data == 'btnSubscribe':
        await button_handler_sub(call)
    elif call.data == 'btnEditProfile':
        await button_handler_edit(call)
    elif call.data == 'btnUnSubscribe':
        await button_handler_unsub(call)
    elif call.data == 'btnSendRequest':
        await button_handler_send_request(call)
    elif call.data == 'btnShowFreeRequests' or call.data == 'btnShowAcceptedRequests' \
            or call.data == 'btnShowMyRequests':
        await show_requests(call)
    elif call.data == 'btnAccept' or call.data == 'btnCompleted' or call.data == 'btnClose':
        await update_request(call)
    elif call.data == 'btnBack' or call.data == 'btnBackUserRequests' or call.data == 'btnBackArtistRequests':
        await back(call)


@dp.message_handler()
async def echo(message: types.Message):
    """
    Эхо обработчик на случай, если пользователь введёт не то что нужно.
    """
    await bot.send_message(message.from_user.id, "Ошибка ввода, попробуйте снова 🧐", reply_markup=nav.menu)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
