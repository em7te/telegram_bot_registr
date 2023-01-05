import sqlite3 as sq


sql_request = sq.connect('sqlite3.db').cursor()

sql_request.execute(
    """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER,
            user_id INTEGER NOT NULL,
            nickname TEXT,
            artist INTEGER NOT NULL,
            update_date TEXT NOT NULL,
            create_date TEXT NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
""")

sql_request.execute(
    """
        CREATE TABLE IF NOT EXISTS requests(
            id INTEGER,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            artist_id INTEGER,
            status TEXT NOT NULL,
            update_date TEXT NOT NULL,
            create_date TEXT NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
""")
