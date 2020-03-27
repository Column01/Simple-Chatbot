# Author: Colin Andress
# Project: Simple Chatbot
# Filename: SlotsGame.py
# Description: The class to execute the slots game

import logging
import random
from threading import Thread

from Database.SQLiteConnector import SQLiteConnector


class SlotsGame(Thread):
    
    def __init__(self, data, conn, chan, settings):
        Thread.__init__(self)
        self.user = data
        self.connection = conn
        self.channel = chan
        self.settings = settings
        self.cost = settings["commands"]["slots"]["cost"]
        self.cooldown = settings["commands"]["slots"]["cooldown"]
        self.reel = settings["commands"]["slots"]["reel"]
        self.jackpot_reward = settings["commands"]["slots"]["jackpot_reward"]
        self.triple_reward = settings["commands"]["slots"]["triple_reward"]
        self.double_reward = settings["commands"]["slots"]["double_reward"]
        self.database = SQLiteConnector()
        self.logger = logging.getLogger("chatbot")
        self.logger.info(f"Started a new slots thread for {self.user.username}")
        
    def run(self):
        user_cooldown = self.database.get_cooldown(self.user.userid, "slots")
        # If they are off cooldown
        if user_cooldown == 0:
            # If they have enough currency to roll the slots
            if self.database.has_enough_currency(self.user.userid, self.cost):
                # Put the user on cooldown, take their money and roll the slots
                self.database.set_cooldown(self.user.userid, "slots", self.cooldown)
                self.database.remove_currency(self.user.userid, self.cost)
                slots = self.roll_slots()
                self.send_message(f'{self.user.username} typed !slots and rolled for {self.cost} coins... {slots[0]} ... {slots[1]} ... {slots[2]} ...')
                # If it's a Jackpot
                if all(x == slots[0] for x in slots) and slots[0] == "KappaPride":
                    self.database.add_currency(self.user.userid, self.jackpot_reward)
                    self.send_message(f'{self.user.username} has hit the jackpot_reward! You win {self.jackpot_reward} coins!')
                    
                # If it's a Triple
                elif all(x == slots[0] for x in slots) and slots[0] != "KappaPride":
                    self.database.add_currency(self.user.userid, self.triple_reward)
                    self.send_message(f'{self.user.username} has gotten 3 of the same emote and won {self.triple_reward} coins!')
    
                # If it's a Double 1 2
                elif slots[0] == slots[1] and slots[1] != slots[2]:
                    self.database.add_currency(self.user.userid, self.double_reward)
                    self.send_message(f'{self.user.username} has gotten 2 of the same emote and won {self.double_reward} coins!')
                    
                # If it's a Double 2 3
                elif slots[1] == slots[2] and slots[1] != slots[0]:
                    self.database.add_currency(self.user.userid, self.double_reward)
                    self.send_message(f'{self.user.username} has gotten 2 of the same emote and won {self.double_reward} coins!')
                    
                # If it's a Double 3 1
                elif slots[0] == slots[2] and slots[0] != slots[1]:
                    self.database.add_currency(self.user.userid, self.double_reward)
                    self.send_message(f'{self.user.username} has gotten 2 of the same emote and won {self.double_reward} coins!')

                # If it's a Loss
                elif slots[0] != slots[1] and slots[0] != slots[2] and slots[2] != slots[1]:
                    self.send_message(f"I'm sorry, {self.user.username}, but you lost!")
                    
                return
            # Not enough currency to play    
            else:
                self.send_message(f"You have insufficient currency, {self.user.username}. The slots requires 100 coins Run !coins to see "
                                   "your balance. You can also run !join to gain some to kick start your earning!")
                return

        # If they are on cooldown, message them the cooldown
        else:
            minutes, seconds = divmod(user_cooldown, 60)
            self.send_message(f"Sorry {self.user.username}. You are on cooldown for {minutes} minutes and {seconds} seconds!")
            return

    def send_message(self, msg):
        self.connection.privmsg(self.channel, msg)

    def roll_slots(self):
        slots_result = []
        for i in range(3):
            # To supress unused warning for i
            del i
            # Picks a random choice from the reel and appends it to an array that gets returned at the end
            slot = random.choice(self.reel)
            slots_result.append(slot)
        return slots_result
