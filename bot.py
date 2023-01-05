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
        await bot.send_message(message.from_user.id, "Стартуем! 🚀", reply_markup=nav.user_menu_in)
    else:
        if [i for i in db.user_type(message.from_user.id)][0][0]:
            await bot.send_message(message.from_user.id, "Бот уже был запущен 🤖", reply_markup=nav.artist_menu_in)
        else:
            await bot.send_message(message.from_user.id, "Бот уже был запущен 🤖", reply_markup=nav.user_menu_in)


# ************************************************************* START /profile
@dp.message_handler(commands=['profile'])
async def profile(message: types.Message):
    """
    Обрабатывает кнопку `Profile`. Отдаёт личные данные.
        Пользователю: id, create_date.
        Художнику: id, nickname, create_date
    """
    if message.message.chat.type == 'private':
        result = db.get_user(message.from_user.id)
        if [i for i in db.user_type(message.from_user.id)][0][0]:
            text = f'Ваши учётные данные:\n\nid: {result[0][1]}\nnickname: {result[0][2]}\ndatetime sub: {result[0][4]}'
            await bot.send_message(message.from_user.id, text, reply_markup=nav.artist_menu_in)
        else:
            text = f'Ваши учётные данные:\n\nid: {result[0][1]}\ndatetime sub: {result[0][4]}'
            await bot.send_message(message.from_user.id, text, reply_markup=nav.user_menu_in)
# ************************************************************* END /profile


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
        if [i for i in db.user_type(call.from_user.id)][0][0]:
            await bot.send_message(call.from_user.id, 'Вы уже художник.', reply_markup=nav.artist_menu_in)
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
        await call.message.reply("Подписка отменена.", reply_markup=nav.user_menu_in)
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
                               reply_markup=nav.artist_menu_in,
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
        if [i for i in db.user_type(call.from_user.id)][0][0]:
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
        await call.message.reply("Редактирование профиля отменено.", reply_markup=nav.artist_menu_in)
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
                               reply_markup=nav.artist_menu_in,
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
        if [i for i in db.user_type(call.from_user.id)][0][0]:
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
        await call.message.reply("Отписка отменена.", reply_markup=nav.artist_menu_in)
        await state.finish()
    else:
        await call.message.reply("Подписка отменена.", reply_markup=nav.user_menu_in)
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
        if [i for i in db.user_type(call.from_user.id)][0][0]:
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
        if [i for i in db.user_type(call.from_user.id)][0][0]:
            # ответ художнику
            await bot.send_message(call.from_user.id, 'Запрос картины отменён.', reply_markup=nav.artist_menu_in)
        else:
            # ответ пользователю
            await bot.send_message(call.from_user.id, 'Запрос картины отменён.', reply_markup=nav.user_menu_in)
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
        type_user = [i for i in db.user_type(message.chat.id)][0][0]
        if type_user:
            await bot.send_message(message.chat.id, bot_answer, reply_markup=nav.artist_menu_in,
                                   parse_mode=ParseMode.MARKDOWN)

            # отправляем всем художникам созданный пользователем/художником запрос на картину
            db_list = db.show_artists()
            bot_answer = f'От пользователя: {message.chat.id}\nОписания запроса: `{text}`'
            [await bot.send_message(i, bot_answer, reply_markup=nav.request_menu_in_not_accept) for i in db_list]
        else:
            await bot.send_message(message.chat.id, bot_answer, reply_markup=nav.user_menu_in,
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
        if message.data == 'btnInShowRequests':
            quantity = 3

            # перебираем выгрузку с БД от `show_requests` и отсеиваем выполненные/закрытые запросы
            result = [i for i in db.show_requests() if i[3] != 'closed' and i[3] != 'completed'][-quantity:]

            for i in range(quantity):
                text = f'id request: {result[i][0]}\n' \
                       f'user id: {result[i][1]}\n' \
                       f'text request: {result[i][2]}\n' \
                       f'date: {result[i][5]}'
                if result[i][3] == 'not accepted':
                    await bot.send_message(message.from_user.id, text, reply_markup=nav.request_menu_in_not_accept)
                if result[i][3] == 'accepted':
                    await bot.send_message(message.from_user.id, text, reply_markup=nav.request_menu_in_accepted)
        elif message.data == 'btnInShowAcceptedRequests':
            quantity = 3

            # то же самое действие, что и выше в `if`
            result = [i for i in db.show_accepted_request(message.from_user.id) if i[3] != 'closed' and i[3] != 'completed'][-quantity:]
            if len(result):
                for i in range(len(result)):
                    text = f'id request: {result[i][0]}\n' \
                           f'user id: {result[i][1]}\n' \
                           f'text request: {result[i][2]}\n' \
                           f'date: {result[i][5]}'
                    if result[i][3] != 'completed' and result[i][3] != 'closed':
                        await bot.send_message(message.from_user.id, text, reply_markup=nav.request_menu_in_accepted)
            else:
                await bot.send_message(message.from_user.id, 'Вы не приняли ни одного запроса',
                                       reply_markup=nav.request_menu_in_accepted)
# ************************************************************* END /show_requests


# ************************************************************* START /update_request
@dp.message_handler(commands=['requests'])
async def update_request(message: types.Message):
    if message.message.chat.type == 'private':
        request_text = message.message.text[12:]
        request_id = request_text[:(request_text.find("u")) - 1]
        if message.data == 'btnInAccept':
            text = 'Вы приняли в работу запрос пользователя'
            db.update_request(message.message.chat.id, 'accepted', request_id)
            await bot.send_message(message.from_user.id, text, reply_markup=nav.request_menu_in_accepted)
        elif message.data == 'btnInClose':
            text = 'Вы закрыли запрос пользователя'
            db.update_request(message.message.chat.id, 'closed', request_id)
            await bot.send_message(message.from_user.id, text, reply_markup=nav.artist_menu_in)
        elif message.data == 'btnInCompleted':
            text = 'Вы успешно завершили запрос пользователя'
            db.update_request(message.message.chat.id, 'completed', request_id)
            await bot.send_message(message.from_user.id, text, reply_markup=nav.artist_menu_in)
# ************************************************************* END /update_request


# ************************************************************* START /update_request
@dp.message_handler(commands=['back'])
async def back(message: types.Message):
    if message.message.chat.type == 'private':
        await bot.send_message(message.from_user.id, 'Menu', reply_markup=nav.artist_menu_in)
# ************************************************************* END /update_request


@dp.callback_query_handler(text_contains='btnIn')
async def btnIn_handler(call: types.CallbackQuery):
    """
    Обрабатывает основные кнопки и перенаправляет на необходимые функции
    """
    if call.data == 'btnInProfile':
        await profile(call)
    elif call.data == 'btnInSubscribe':
        await button_handler_sub(call)
    elif call.data == 'btnInEditProfile':
        await button_handler_edit(call)
    elif call.data == 'btnInUnSubscribe':
        await button_handler_unsub(call)
    elif call.data == 'btnInSendRequest':
        await button_handler_send_request(call)
    elif call.data == 'btnInShowRequests' or call.data == 'btnInShowAcceptedRequests':
        await show_requests(call)
    elif call.data == 'btnInAccept' or call.data == 'btnInCompleted' or call.data == 'btnInClose':
        await update_request(call)
    elif call.data == 'btnInBack':
        await back(call)


@dp.message_handler()
async def echo(message: types.Message):
    """
    Эхо обработчик на случай, если пользователь введёт не то что нужно.
    """
    if [i for i in db.user_type(message.from_user.id)][0][0]:
        await bot.send_message(message.from_user.id, "Ошибка ввода, попробуйте снова 🧐",
                               reply_markup=nav.artist_menu_in)
    else:
        await bot.send_message(message.from_user.id, "Ошибка ввода, попробуйте снова 🧐",
                               reply_markup=nav.user_menu_in)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
