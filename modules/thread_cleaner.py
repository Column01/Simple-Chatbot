from threading import Thread
import logging

class ThreadCleaner(Thread):
    
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