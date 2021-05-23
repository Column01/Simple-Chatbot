# Author: Colin Andress
# Project: Simple Chatbot
# Filename: thread_cleaner.py
# Description: The class to clean game threads from memory

import logging
from threading import Thread


class ThreadCleaner(Thread):
    """Cleans up dice game threads from the queue if they are complete"""
    def __init__(self, bot_instance):
        Thread.__init__(self)
        self.twitch_bot_instance = bot_instance
        self.logger = logging.getLogger("chatbot")
    
    def run(self):
        while True:
            if len(self.twitch_bot_instance.dice_games) > 0:
                for thread in self.twitch_bot_instance.dice_games:
                    if not thread.is_alive():
                        self.logger.info("Dice game thread finished executing so we're gonna remove it now.")
                        self.twitch_bot_instance.dice_games.remove(thread)
