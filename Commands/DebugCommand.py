# Author: Colin Andress
# Project: Simple Chatbot
# Filename: DebugCommand.py
# Description: The class to execute the debug command

import logging
from threading import Thread


class DebugCommand(Thread):
    """Debug command, prints message tags and some misc info to the log"""
    def __init__(self, data, conn, chan, _, e):
        Thread.__init__(self)
        self.user = data
        self.connection = conn
        self.channel = chan
        self.e = e
        self.logger = logging.getLogger("chatbot")
        
    def run(self):
        if self.user.is_broadcaster or self.user.is_mod:
            print(f'Recieved Debug command from {self.user.username}... Logging tags to log file')
            self.send_message("I logged the tags to the chatbot log. "
                              "I hope you were asked to run this "
                              "or you wanted to debug something")
            json_tags = str(self.e.tags).replace("'", '"')
            self.logger.info(f"User Tags: {json_tags}\n"
                             f"Recieved Message: {self.e.arguments[0]}\n"
                             f"Connected Channel: {self.channel}\n")
        else:
            self.send_message(f"You are not authorized to use the debug command, {self.user.username}. "
                              "Please ask the streamer for permission if you believe this is "
                              "an error.")
    
    def send_message(self, msg):
        self.connection.privmsg(self.channel, msg)
