import sqlite3
import time

# Connect to SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users(userid INT, username TEXT, currency INT, joincmd INT, slotscmd INT)")
conn.commit()


# Reads the user's entire info. Mostly used in development but may be used as a patch method for commands
# who refuse to work.
def read_username(userid, username):
    c.execute("SELECT username,userid FROM users WHERE userid = ?", (userid,))
    user = c.fetchone()
    return user


# Reads if the user is on cooldown
def read_cooldown(userid, game):

    c.execute("SELECT "+game+",userid FROM users WHERE userid = ?", (userid,))
    cooldownfetch = c.fetchone()
    currenttime = int(time.time())
    if cooldownfetch is not None:
        # and the cooldown is expired, set oncooldown to False
        if cooldownfetch[0] <= currenttime:
            oncooldown = False
        # if the cooldown is not expired, set oncooldown to True
        else:
            oncooldown = True
            cooldownremainder = int((cooldownfetch[0] - currenttime) / 60)
            return oncooldown, cooldownremainder
    # If the user does not exist, set oncooldown to None
    else:
        oncooldown = None
    return oncooldown


def read_currency(userid):
    c.execute("SELECT currency,userid FROM users where userid = ?", (userid,))
    currencyfetch = c.fetchone()
    if currencyfetch is not None:
        currency = currencyfetch[0]
    else:
        currency = 0
    return currency
