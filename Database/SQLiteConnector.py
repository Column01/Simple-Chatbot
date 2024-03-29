# Author: Colin Andress
# Project: Simple Chatbot
# Filename: SQLiteConnector.py
# Description: SQLite database connector class

import logging
import sqlite3
import time

import modules.helpers as helpers


class SQLiteConnector:
    
    def __init__(self):
        """The SQLite connector class, handles all database interaction in the bot."""
        self.logger = logging.getLogger("chatbot")
        self.conn = sqlite3.connect('users.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users(userid INT, username TEXT, currency INT, _join INT, _slots INT, _dice INT, color TEXT)")
        self.conn.commit()
        self.cursor.execute("PRAGMA table_info('users')")
        databaselist = self.cursor.fetchall()
        columnlist = ["userid", "username", "currency", "_join", "_slots", "_dice", "color"]
        for item in columnlist:
            i = columnlist.index(item)
            try:
                if item in databaselist[i][1]:
                    pass
            except IndexError:
                self.cursor.execute("ALTER TABLE users ADD COLUMN " + item + " INT")
                self.logger.info(f"Added new game table {item}")
            self.conn.commit()

    def get_username(self, userid):
        """Gets the username of the specified userID from the database
        Parameters:
            userid -- The userID of the user you want to check
        Returns:
            String -- The user's name
        """
        self.cursor.execute("SELECT username FROM users WHERE userid = ?", (userid,))
        user = self.cursor.fetchone()
        if user is not None:
            if helpers.test_list_item(user, 0):
                return user[0]

    def get_cooldown(self, userid, game):
        """Gets the cooldown for the specified userid and game
        Parameters:
            userid -- The userID of the user you want to check
            game -- The name of the game for which the cooldown is being checked
        Returns:
            Integer -- The cooldown in seconds
        """
        self.cursor.execute("SELECT _" + game + ", userid FROM users WHERE userid = ?", (userid,))
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
    
    def get_currency(self, userid):
        """Get the amount of currency the user has.
        Parameters:
            userid -- The userID of the user you want to check
        Returns:
            Integer -- The amount of currency the user has
        """
        self.cursor.execute("SELECT currency, userid FROM users WHERE userid = ?", (userid,))
        currencyfetch = self.cursor.fetchone()
        if currencyfetch is not None:
            currency = currencyfetch[0]
        else:
            currency = 0
        return currency
    
    def update_username(self, userid, username):
        """Updates the user's username in the database
        Parameters:
            userid -- The userID of the user
            username -- The current username of the user (from twitch chat)
        """
        usernamedb = self.get_username(userid)
        if usernamedb is None:
            self.logger.info(f'Adding {username} to database...')
            self.add_user(userid, username, 0)
        elif username != usernamedb:
            self.logger.info(f'{username} has mismatched usernames. Updating.')
            self.cursor.execute("UPDATE users SET username = ? WHERE userid = ?", (username, userid))
            self.conn.commit()
            self.logger.info("Updated username into database")
    
    def add_user(self, userid, username, currency):
        """Adds the user to the database
        Parameters:
            userid -- The userID of the user
            username -- The username of the user
            currency -- The amount of currency they will start out with as an integer
        """
        self.cursor.execute("INSERT INTO users (userid, username, currency, _join, _slots, _dice) VALUES (?, ?, ?, ?, ?, ?)",
                            (userid, username, currency, 0, 0, 0))
        self.conn.commit()
    
    def add_currency(self, userid, amount):
        """Adds the currency for the userID in the database
        Parameters:
            userid -- The userID of the user you want to add currency to
            amount -- The amount of currency you want to add as an integer
        """
        currency_db = self.get_currency(userid)
        new_currency = amount + currency_db
        self.cursor.execute("UPDATE users SET currency = ? WHERE userid = ?", (new_currency, userid))
        self.conn.commit()
        username = self.get_username(userid)
        self.logger.info(f"Added {amount} currency to {username}")
    
    def set_cooldown(self, userid, game, cooldown):
        """Sets the user's cooldown for the specified game
        Parameters:
            userid -- The userID of the user you want to add currency to
            game - The name of the game to add the cooldown for
            cooldown -- The cooldown length in seconds as an integer
        """
        new_cooldown = int(time.time()) + cooldown
        self.cursor.execute("UPDATE users SET _" + game + " = ? WHERE userid = ?", (new_cooldown, userid))
        self.conn.commit()
        username = self.get_username(userid)
        self.logger.info(f"Put {username} on cooldown for {game} for {cooldown} seconds")

    def remove_currency(self, userid, amount):
        """Remove the specified amount of currency from the user
        Parameters:
            userid -- The userID of the user you want to remove currency from
            amount - The amount of currency to remove as an integer
        Returns:
            Boolean -- Whether or not they had enough currency to remove
        """
        currency_db = self.get_currency(userid)
        if self.has_enough_currency(userid, amount):
            new_currency = currency_db - amount
            self.cursor.execute("UPDATE users SET currency = ? WHERE userid = ?", (new_currency, userid))
            self.conn.commit()
            username = self.get_username(userid)
            self.logger.info(f"Removed {amount} currency from {username}")
            return True
        else:
            return False
       
    def has_enough_currency(self, userid, amount):
        """Check if the user has enough currency to do something
        Parameters:
            userid -- The userID of the user you want to check
            amount - The amount of currency to check if they have as an integer
        Returns:
            Boolean -- Whether or not they have enough currency
        """
        currency_db = self.get_currency(userid)
        return currency_db >= amount
    
    def get_user_color(self, userid):
        """Get the user's chat color
        Parameters:
            userid -- The userID of the user to get the color for
        
        Returns:
            String -- The Hex color code value for the user
            
            NoneType -- If the color is not set in the database
        """
        self.cursor.execute("SELECT color, userid FROM users WHERE userid = ?", (userid,))
        color = self.cursor.fetchone()
        if color is None:
            return color
        if helpers.test_list_item(color, 0):
            return color[0]

    def set_user_color(self, userid, hex_value):
        """Sets the user's color in the database
        Parameters:
            userid -- The userID of the user you want to set the color for
            hex_value - The hex color code as a string
        """
        self.cursor.execute("UPDATE users SET color = ? WHERE userid = ?", (hex_value, userid))
        self.conn.commit()
        username = self.get_username(userid)
        self.logger.info(f"Set {username}'s color to {hex_value}")

    def clear_colors(self):
        """Wipes the user colors from the database
        Called when the chatbot is exited.
        This means users will have a random color each time in console to emulate what twitch does on their frontend.
        """
        self.cursor.execute("UPDATE users SET color = Null")
        self.conn.commit()
        self.logger.info("Set all user colors to Null.")
