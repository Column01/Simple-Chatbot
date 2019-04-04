import sqlite3
import time
conn = sqlite3.connect('users.db')
c = conn.cursor()


def update_username(userid, username):
    c.execute("UPDATE users SET username = ? WHERE userid = ?", (username, userid))
    conn.commit()
    print("Updated username into database")
    return


# Adds the user if they don't exist
def add_user(userid, username, currency, commandname, cooldown):
    c.execute("SELECT userid FROM users WHERE userid = ?", (userid,))
    user = c.fetchone()
    c.execute("INSERT INTO users (userid, username, currency, joincmd, slotscmd) VALUES (?, ?, ?, ?, ?)",
                (userid, username, currency, cooldown, '0'))
    conn.commit()


# add's currency and cooldown onto the user
def add_currency(userid, currency, currencydb):
    new_currency = currency + currencydb
    c.execute("UPDATE users SET currency = ? WHERE userid = ?", (new_currency, userid))
    conn.commit()
    return


def add_cooldown(userid, game, cooldown):
    new_cooldown = int(time.time()) + cooldown
    c.execute("UPDATE users SET "+game+" = ? WHERE userid = ?", (new_cooldown, userid,))
    conn.commit()
    return
