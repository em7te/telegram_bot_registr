from aiogram.dispatcher.filters.state import State, StatesGroup


class FormSub(StatesGroup):
    artist = State()
    nickname = State()


class FormEdit(StatesGroup):
    nickname = State()


class FormUnSub(StatesGroup):
    artist = State()


class FormSendReq(StatesGroup):
    text = State()
