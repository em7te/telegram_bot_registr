import sqlite3
from datetime import datetime
from aiogram.dispatcher.filters.state import State, StatesGroup


class FormSub(StatesGroup):
    artist = State()
    nickname = State()


class FormEdit(StatesGroup):
    nickname = State()


class FormUnSub(StatesGroup):
    artist = State()


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id):
        with self.connection:
            datetime_now = str(datetime.now())[:19]
            self.cursor.execute(
                "INSERT INTO `users` (`user_id`, `artist`, `update_date`, `create_date`) VALUES (?, 0, ?, ?)",
                (user_id, datetime_now, datetime_now,)
            )

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def user_type(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `artist` FROM `users` WHERE `user_id` = ?", (user_id,))

    def get_user(self, user_id):
        with self.connection:
            request_sql = self.cursor.execute("SELECT * FROM `users` WHERE user_id = ?", (user_id,))
            return [row for row in request_sql]  # output: [(`id`, `user_id`, `nickname`, `artist`, `update`, `create`)]

    def update_artist(self, artist, user_id):
        with self.connection:
            datetime_now = str(datetime.now())[:19]
            self.cursor.execute("""UPDATE `users` SET `artist` = ?, `update_date` = ? WHERE user_id = ?""",
                                (artist, datetime_now, user_id))

    def update_nickname(self, nickname, user_id):
        with self.connection:
            datetime_now = str(datetime.now())[:19]
            self.cursor.execute("""UPDATE `users` SET `nickname` = ?, `update_date` = ? WHERE user_id = ?""",
                                (nickname, datetime_now, user_id))
