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
from db.sql import Database, FormSub, FormEdit, FormUnSub


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
