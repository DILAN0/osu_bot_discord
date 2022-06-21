import sqlite3
import os.path

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

def check_file():
    if os.path.exists("../osu-discord-bot/osubot.db") == True:
        print("Data File ✓")
    if os.path.exists("../osu-discord-bot/osubot.db") == False:
        print("Data File ╳")
        data()
