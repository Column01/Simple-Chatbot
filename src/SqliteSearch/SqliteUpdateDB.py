import sqlite3
import time
try:
    from SqliteSearch import SqliteReadDB
except ImportError:
    import SqliteReadDB
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users(userid INT, username TEXT, currency INT, _join INT, _slots INT)")
conn.commit()


# Called from the main script to update a mismatched username
def update_username(userid, username):
    c.execute("UPDATE users SET username = ? WHERE userid = ?", (username, userid))
    conn.commit()
    print("Updated username into database")
    return


# Adds the user with some cookie cutter data (provided from main script)
def add_user(userid, username, currency, joincooldown, slotscooldown):
    c.execute("INSERT INTO users (userid, username, currency, _join, _slots) VALUES (?, ?, ?, ?, ?)",
              (userid, username, currency, joincooldown, slotscooldown))
    conn.commit()
    return


# add's currency and cooldown onto the user
def add_currency(userid, currency):
    currencydb = SqliteReadDB.read_currency(userid)
    new_currency = currency + currencydb
    c.execute("UPDATE users SET currency = ? WHERE userid = ?", (new_currency, userid))
    conn.commit()
    return


def add_cooldown(userid, game, cooldown):
    new_cooldown = int(time.time()) + cooldown
    c.execute("UPDATE users SET _"+game+" = ? WHERE userid = ?", (new_cooldown, userid,))
    conn.commit()
    return
