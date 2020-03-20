# Author: Colin Andress
# Project: Simple Chatbot
# Filename: SqliteReadDB.py
# Purpose: Reads data from the SQLite DB file. Called from various scripts.
import sqlite3
import time
import modules.helpers as helpers

# Connect to SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users(userid INT, username TEXT, currency INT, _join INT, _slots INT)")
conn.commit()


# Reads the user's entire info. Mostly used in development but may be used as a patch method for commands
# who refuse to work.
def read_username(userid):
    c.execute("SELECT username FROM users WHERE userid = ?", (userid,))
    user = c.fetchone()
    return user


# Reads if the user is on cooldown
def read_cooldown(userid, game):
    c.execute("SELECT _"+game+",userid FROM users WHERE userid = ?", (userid,))
    cooldownfetch = c.fetchone()
    currenttime = int(time.time())
    if cooldownfetch is not None:
        if helpers.test_list_item(cooldownfetch, 0):
            cooldownfetch = cooldownfetch[0]
        # if the cooldown is expired, set oncooldown to False
        if cooldownfetch <= currenttime:
            oncooldown = False
        # if the cooldown is not expired, set oncooldown to True
        else:
            cooldownremainder = cooldownfetch - currenttime
            return cooldownremainder
    # If the user does not exist, set oncooldown to None
    else:
        oncooldown = False
    return oncooldown


def read_currency(userid):
    c.execute("SELECT currency,userid FROM users where userid = ?", (userid,))
    currencyfetch = c.fetchone()
    if currencyfetch is not None:
        currency = currencyfetch[0]
    else:
        currency = 0
    return currency
