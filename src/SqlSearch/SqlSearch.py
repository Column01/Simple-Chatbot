import sqlite3
import time

# Connect to SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users(userid INT, username TEXT, currency INT, joincmd INT, slotscmd INT)")
conn.commit()


class SqlSearch:
    # Adds the user if they don't exist
    def add_user(userid, username, currency, commandname, cooldown):
        c.execute("SELECT userid FROM users WHERE userid = ?", (userid,))
        user = c.fetchone()
        if user is None:
            c.execute("INSERT INTO users (userid, username, currency, joincmd, slotscmd) VALUES (?, ?, ?, ?, ?)",
                      (userid, username, currency, cooldown, '0'))
            conn.commit()
            addeduser = True
        else:
            addeduser = False
        return addeduser

    # Reads the user's info
    def read_user(userid):
        c.execute("SELECT * FROM users WHERE userid = ?", (userid,))
        row = c.fetchone()
        return row

    # Reads if the user is on cooldown
    def read_cooldown(userid, commandname):
        c.execute("SELECT joincmd,userid FROM users WHERE userid = ?", (userid,))
        cooldownfetch = c.fetchone()
        print(cooldownfetch)
        currenttime = int(time.time())
        # If the user exists
        if cooldownfetch is not None:
            # and the cooldown is expired, set oncooldown to False
            if cooldownfetch[0] <= currenttime:
                oncooldown = False
            # if the cooldown is not expired, set oncooldown to True
            else:
                oncooldown = True
        # If the user does not exist, set oncooldown to None
        else:
            oncooldown = None
        return oncooldown
