import sqlite3

conn = sqlite3.connect("../osubot.db")
cursor = conn.cursor()

def data():
    cursor.execute("""CREATE TABLE "users" (
                "id"	INT,
                "nickname"	TEXT,
                "mention"	TEXT,
                "account"	TEXT,
                "steam"  TEXT,
                "osu"  TEXT,
                "pp"  INT
            )""")
    conn.commit()