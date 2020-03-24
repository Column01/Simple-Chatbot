import sqlite3
import modules.helpers as helpers
import time
import logging

class SQLiteConnector:
    
    def __init__(self):
        self.logger = logging.getLogger("chatbot")
        self.conn = sqlite3.connect('users.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users(userid INT, username TEXT, currency INT, _join INT, _slots INT, _dice INT)")
        self.conn.commit()
        self.cursor.execute("PRAGMA table_info('users')")
        databaselist = self.cursor.fetchall()
        columnlist = ["userid", "username", "currency", "_join", "_slots", "_dice"]
        for item in columnlist:
            i = columnlist.index(item)
            try:
                if item in databaselist[i][1]:
                    pass
            except IndexError:
                self.cursor.execute("ALTER TABLE users ADD COLUMN " + item + " INT")
                self.logger.info(f"Added new game table {item}")
            self.conn.commit()

    """Gets the username of the specified userID from the database
    Parameters:
        userid -- The userID of the user you want to check
    Returns:
        String -- The user's name
    """    
    def get_username(self, userid):
        self.cursor.execute("SELECT username FROM users WHERE userid = ?", (userid,))
        user = self.cursor.fetchone()
        if user is not None:
            if helpers.test_list_item(user, 0):
                return user[0]

    """Gets the cooldown for the specified userid and game
    Parameters:
        userid -- The userID of the user you want to check
        game -- The name of the game for which the cooldown is being checked
    Returns:
        Integer -- The cooldown in seconds
    """    
    def get_cooldown(self, userid, game):
        self.cursor.execute("SELECT _"+game+",userid FROM users WHERE userid = ?", (userid,))
        cooldown_fetch = self.cursor.fetchone()
        current_time = int(time.time())
        if cooldown_fetch is not None:
            if helpers.test_list_item(cooldown_fetch, 0):
                cooldown_fetch = cooldown_fetch[0]
            # if the cooldown is expired, return 0 for not on cooldown.
            if cooldown_fetch <= current_time:
                return 0
            # if the cooldown is not expired, return the remainder of the cooldown in seconds.
            else:
                cooldownremainder = cooldown_fetch - current_time
                return cooldownremainder
        # If the user does not exist, return 0 for the cooldown
        else:
            return 0
    
    """Get the amount of currency the user has.
    Parameters:
        userid -- The userID of the user you want to check     
    Returns:
        Integer -- The amount of currency the user has
    """    
    def get_currency(self, userid):
        self.cursor.execute("SELECT currency,userid FROM users where userid = ?", (userid,))
        currencyfetch = self.cursor.fetchone()
        if currencyfetch is not None:
            currency = currencyfetch[0]
        else:
            currency = 0
        return currency
    
    """Updates the user's username in the database
    Parameters:
        userid -- The userID of the user
        username -- The current username of the user (from twitch chat)
    """    
    def update_username(self, userid, username):
        usernamedb = self.get_username(userid)
        if usernamedb is None:
            self.logger.info(f'Adding {username} to database...')
            self.add_user(userid, username, 0)
            return
        elif username == usernamedb[0]:
            return
        elif username != usernamedb[0]:
            self.logger.info(f'{username} has mismatched usernames. Updating.')
            self.cursor.execute("UPDATE users SET username = ? WHERE userid = ?", (username, userid))
            self.conn.commit()
            self.logger.info("Updated username into database")
            return
    
    """Adds the user to the database
    Parameters:
        userid -- The userID of the user
        username -- The username of the user
        currency -- The amount of currency they will start out with as an integer
    """
    def add_user(self, userid, username, currency):
        self.cursor.execute("INSERT INTO users (userid, username, currency, _join, _slots, _dice) VALUES (?, ?, ?, ?, ?, ?)",
                (userid, username, currency, 0, 0, 0))
        self.conn.commit()
        return
    
    """Adds the currency for the userID in the database
    Parameters:
        userid -- The userID of the user you want to add currency to
        amount -- The amount of currency you want to add as an integer
    """
    def add_currency(self, userid, amount):
        currency_db = self.get_currency(userid)
        new_currency = amount + currency_db
        self.cursor.execute("UPDATE users SET currency = ? WHERE userid = ?", (new_currency, userid))
        self.conn.commit()
        username = self.get_username(userid)
        self.logger.info(f"Added {amount} currency to {username}")
        return
    
    """Sets the user's cooldown for the specified game
    Parameters:
        userid -- The userID of the user you want to add currency to
        game - The name of the game to add the cooldown for
        cooldown -- The cooldown length in seconds as an integer
    """
    def set_cooldown(self, userid, game, cooldown):
        new_cooldown = int(time.time()) + cooldown
        self.cursor.execute("UPDATE users SET _"+game+" = ? WHERE userid = ?", (new_cooldown, userid,))
        self.conn.commit()
        username = self.get_username(userid)
        self.logger.info(f"Put {username} on cooldown for {game} for {cooldown} seconds")
        return
    
    """Remove the specified amount of currency from the user
    Parameters:
        userid -- The userID of the user you want to remove currency from
        amount - The amount of currency to remove as an integer
    Returns:
        Boolean -- Whether or not they had enough currency to remove
    """    
    def remove_currency(self, userid, amount):
        currency_db = self.get_currency(userid)
        if self.has_enough_currency(userid, amount):
            new_currency = currency_db - amount
            self.cursor.execute("UPDATE users SET currency = ? WHERE userid = ?", (new_currency, userid,))
            self.conn.commit()
            username = self.get_username(userid)
            self.logger.info(f"Removed {amount} currency from {username}")
            return True
        else:
            return False
    
    """Check if the user has enough currency to do something
    Parameters:
        userid -- The userID of the user you want to check
        amount - The amount of currency to check if they have as an integer
    Returns:
        Boolean -- Whether or not they have enough currency
    """    
    def has_enough_currency(self, userid, amount):
        currency_db = self.get_currency(userid)
        if currency_db >= amount:
            return True
        else:
            return False