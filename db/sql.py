import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id):
        with self.connection:
            datetime_now = str(datetime.now())[:19]
            self.cursor.execute(
                """INSERT INTO `users` (`user_id`, `artist`, `update_date`, `create_date`) VALUES (?, 0, ?, ?)""",
                (user_id, datetime_now, datetime_now,))

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

    def add_request(self, text, user_id):
        with self.connection:
            datetime_now = str(datetime.now())[:19]
            status = 'not accepted'
            self.cursor.execute(
                """INSERT INTO `requests` (`user_id`, `text`, `status`, `update_date`, `create_date`) 
                VALUES (?, ?, ?, ?, ?)""",
                (user_id, text, status, datetime_now, datetime_now))

    def all_artists(self):
        with self.connection:
            db_list = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `artist` = 1")
            result = [j[0] for j in [i for i in db_list]]
            return result


# db = Database("db/sqlite3.db")
# result = [j[0] for j in [i for i in db.all_artists()]]
# print(db.all_artists())

