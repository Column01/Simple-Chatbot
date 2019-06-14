# Author: Colin Andress
# Project: Simple Chatbot
# Filename: SqliteReadDB.py
# Purpose: Updates data in the SQLite DB file. Called from various scripts.
import sqlite3
import time
import modules.SqliteReadDB as SqliteReadDB
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users(userid INT, username TEXT, currency INT, _join INT, _slots INT, _dice INT)")
conn.commit()
c.execute("PRAGMA table_info('users')")
databaselist = c.fetchall()
columnlist = ["userid", "username", "currency", "_join", "_slots", "_dice"]
for item in columnlist:
    i = columnlist.index(item)
    try:
        if item in databaselist[i][1]:
            pass
    except IndexError:
        c.execute("ALTER TABLE users ADD COLUMN " + item + " INT")
        print("Added new game table {}".format(item))
    conn.commit()


# Called from the main script to update a mismatched username
def update_username(userid, username):
    usernamedb = SqliteReadDB.read_username(userid)
    if usernamedb is None:
        print('Adding ' + username + ' to database...')
        add_user(userid, username, 0, 0, 0, 0)
        return
    elif username == usernamedb:
        return
    elif username != usernamedb:
        print(username + ' has mismatched usernames. Updating.')
        c.execute("UPDATE users SET username = ? WHERE userid = ?", (username, userid))
        conn.commit()
        print("Updated username into database")
        return


# Adds the user with some cookie cutter data (provided from main script)
def add_user(userid, username, currency, joincooldown, slotscooldown, dicecooldown):
    c.execute("INSERT INTO users (userid, username, currency, _join, _slots, _dice) VALUES (?, ?, ?, ?, ?, ?)",
              (userid, username, currency, joincooldown, slotscooldown, dicecooldown))
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


def cost_subtract(userid, cost):
    currencydb = SqliteReadDB.read_currency(userid)
    if currencydb >= cost:
        new_currency = currencydb - cost
        c.execute("UPDATE users SET currency = ? WHERE userid = ?", (new_currency, userid,))
        conn.commit()
        return True
    else:
        return False
