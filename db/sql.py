import sqlite3
from datetime import datetime
from pprint import pprint


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
            request_sql = self.cursor.execute("SELECT `artist` FROM `users` WHERE `user_id` = ?", (user_id,))
            return [i for i in request_sql]

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

    def show_artists(self):
        with self.connection:
            db_list = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `artist` = 1")
            result = [j[0] for j in [i for i in db_list]]
            return result

    def show_requests(self):
        with self.connection:
            db_list = self.cursor.execute("SELECT `id`, `user_id`, `text`, `status`, `update_date`, `create_date`"
                                          "FROM `requests`")
            result = [i for i in db_list]
            return result

    def show_my_requests(self, my_id):
        with self.connection:
            db_list = self.cursor.execute("SELECT `id`, `user_id`, `text`, `status`, `update_date`, `create_date`"
                                          "FROM `requests` WHERE `user_id` = ?", (my_id,))
            result = [i for i in db_list]
            return result

    def show_accepted_request(self, artist_id):
        with self.connection:
            db_list = self.cursor.execute("SELECT `id`, `user_id`, `text`, `status`, `update_date`, `create_date`"
                                          "FROM `requests` WHERE `artist_id` = ?", (artist_id,))
            result = [i for i in db_list]
            return result

    def update_request(self, user_id, status, request_id):
        with self.connection:
            datetime_now = str(datetime.now())[:19]
            self.cursor.execute("""UPDATE `requests` SET `artist_id` = ?, status = ?, `update_date` = ? 
            WHERE `id` = ?""", (user_id, status, datetime_now, request_id))


# db = Database("db/sqlite3.db")
# x = db.show_requests()
# result = [i for i in db.show_requests() if i[3] != 'closed' and i[3] != 'completed'][-3:]
# pprint(result)

