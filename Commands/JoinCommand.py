# Author: Colin Andress
# Project: Simple Chatbot
# Filename: JoinCommand.py
# Description: The class to execute the join command

import logging
from threading import Thread

from Database.SQLiteConnector import SQLiteConnector


class JoinCommand(Thread):
    
    # Probably overkill to use a thread for this but why not
    def __init__(self, data, conn, chan, settings):
        Thread.__init__(self)
        self.user = data
        self.settings = settings
        self.connection = conn
        self.channel = chan
        self.reward = settings['commands']['join']['join_reward']
        self.cooldown = settings['commands']['join']['join_cooldown']
        self.success_message = settings['commands']['join']['success_message']
        self.cooldown_message = settings['commands']['join']['cooldown_message']
        self.database = SQLiteConnector()
        self.logger = logging.getLogger("chatbot")
        self.logger.info(f"Started a new Join command thread for {self.user.username}")

    def run(self):
        user_cooldown = self.database.get_cooldown(self.user.userid, "join")
        # If the user is off cooldown
        if user_cooldown == 0:
            # Add currency and send the message
            self.database.add_currency(self.user.userid, self.reward)
            self.database.set_cooldown(self.user.userid, "join", self.cooldown)
            self.send_message(self.success_message.format(username=self.user.username, reward=self.reward,
                                                          command="join"))
            return
        else:
            # Send a message with the cooldown remainder
            minutes, seconds = divmod(user_cooldown, 60)
            self.send_message(self.cooldown_message.format(username=self.user.username, minutes=minutes,
                                                           seconds=seconds))
            return
    
    def send_message(self, msg):
        self.connection.privmsg(self.channel, msg)
