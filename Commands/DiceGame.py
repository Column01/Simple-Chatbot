# Author: Colin Andress
# Project: Simple Chatbot
# Filename: DiceGame.py
# Description: The class to execute the dice game

import logging
import random
from threading import Thread
from timeit import default_timer as timer

from Database.SQLiteConnector import SQLiteConnector


class DiceGame(Thread):
    """Dice game"""
    def __init__(self, data, cmd, bot_instance):
        Thread.__init__(self)
        self.instance = bot_instance
        self.usage = "Use \"!dice <opponent name> <bet>\" to start a game or \"!dice accept\" to accept a battle."
        self.settings = self.instance.settings
        self.connection = self.instance.connection
        self.channel = self.instance.channel
        self.cmd = cmd
        self.waiting_for_accept = True
        self.player_one = data
        if len(cmd) == 3 and int(cmd[2]) > 0:
            self.wager = int(cmd[2])
        else:
            self.wager = -1
        self.player_to_wait_for = cmd[1]
        self.player_two = None
        self.database = SQLiteConnector()
        self.cooldown = self.settings["commands"]["dice"]["cooldown"]
        self.logger = logging.getLogger("chatbot")
        self.logger.info(f"Started a new dice game thread for {self.player_one.username} versus {self.player_to_wait_for}")

    def run(self):
        self.start_game()

    def start_game(self):
        # Check if the game is valid
        if not self.is_valid_game():
            return
        self.send_message(f"Hey @{self.player_to_wait_for}! "
                          f"{self.player_one.username} has challenged you to a dice battle for {self.wager} coins. "
                          "Type \"!dice accept\" to accept the dice battle! Request will expire in 60 seconds.")
        start_time = timer()
        # Loop to wait for the second player to accept the duel.
        while self.waiting_for_accept:
            timer_duration = int(timer() - start_time)
            if timer_duration >= 60:
                self.waiting_for_accept = None
        # waiting for accept is changed externally when the second user accepts the battle.
        if self.waiting_for_accept is False:
            # Check if player two can afford to battle, and if they can't, tell them and end the game.
            p_two_cost_check = self.database.has_enough_currency(self.player_two.userid, self.wager)
            if not p_two_cost_check:
                self.send_message(f"{self.player_two.username} does not have enough currency to battle. Please bet an amount that you both can afford and try again.")
                return
            # Put player one on cooldown since they started the battle
            self.database.set_cooldown(self.player_one.userid, "dice", self.cooldown)
            # Load the min and max dice values and roll the dice
            dice_min = self.settings["commands"]["dice"]["min_num"]
            dice_max = self.settings["commands"]["dice"]["max_num"]
            player_one_roll = random.randint(dice_min, dice_max)
            player_two_roll = random.randint(dice_min, dice_max)
            # If the rools are the same value, re-roll until they are different values
            if player_one_roll == player_two_roll:
                while player_one_roll == player_two_roll:
                    player_one_roll = random.randint(dice_min, dice_max)
                    player_two_roll = random.randint(dice_min, dice_max)
            self.send_message(f"Rolling the dice... {self.player_one.username} rolled {player_one_roll}... {self.player_two.username} rolled {player_two_roll}...")
            if player_one_roll > player_two_roll:
                # Player one wins the dice roll. Give them their winings
                self.database.add_currency(self.player_one.userid, self.wager)
                # Remove player two's wager since they lost
                self.database.remove_currency(self.player_two.userid, self.wager)
                self.send_message(f"Congratulations {self.player_one.username}! You won the battle and won {self.wager} coins!")
            elif player_two_roll > player_one_roll:
                # Player two wins the dice roll. Give them their winings
                self.database.add_currency(self.player_two.userid, self.wager)
                # Remove player one's wager since they lost
                self.database.remove_currency(self.player_one.userid, self.wager)
                self.send_message(f"Congratulations {self.player_two.username}! You won the battle and won {self.wager} coins!")
        # This happens when the timer expires on the dice battle.
        elif self.waiting_for_accept is None:
            self.send_message(f"Sorry, {self.player_one.username}. The game timer expired while waiting for {self.player_to_wait_for} to accept the dice battle.")

    def is_valid_game(self):
        """Checks various things to see if the game can progress
        Returns:
            Boolean -- If the game is valid or not
        """
        player_one_cooldown = self.database.get_cooldown(self.player_one.userid, "dice")
        # Player one is on cooldown still
        if player_one_cooldown != 0:
            minutes, seconds = divmod(player_one_cooldown, 60)
            self.send_message(f"Sorry, {self.player_one.username}. You are still on cooldown for {minutes} minutes and {seconds} seconds.")
            return False
        # User is challenging themselves
        elif self.is_challenging_self():
            self.send_message(f"Sorry, {self.player_one.username}. You cannot dice battle yourself! Please specify another user, you lonely goof. {self.usage}")
            return False
        # Invalid bet
        elif self.wager == -1:
            self.send_message(f"Sorry, {self.player_one.username}. You must enter a bet that is more than zero. {self.usage}")
            return False
        # Player one cannot afford to play
        elif not self.database.has_enough_currency(self.player_one.userid, self.wager):
            self.send_message(f"I'm sorry, {self.player_one.username}, but you do not have enough currency to bet that much. Please check your balance with !coins")
            return False
        # Player two is not in chat
        elif not self.is_player_two_in_chat():
            self.send_message(f"Sorry, {self.player_one.username}, that user is not currently in chat. Please try again when they are online next!")
            return False
        else:
            return True

    def is_player_two_in_chat(self):
        """Checks if player two is present in the chat
        Returns:
            Boolean -- Whether or not player two is in the chat
        """
        return self.player_to_wait_for.lower() in self.instance.get_users()

    def is_challenging_self(self):
        """Checks whether the user is challenging themself to a dice battle.
        Returns:
            Boolean -- Whether or not they challenged themselves
        """
        return self.player_one.username.lower() == self.player_to_wait_for.lower()
    
    def send_message(self, msg):
        """Sends a chat message to the channel"""
        self.connection.privmsg(self.channel, msg)
    
    def check_player_two(self, data):
        """pubmsg event for each dice game.
        Returns:
            Boolean -- Returns whether or not the player was the one we were waiting for in this dice game.
        """
        if data.username.lower() == self.player_to_wait_for.lower():
            self.player_two = data
            self.waiting_for_accept = False
            return True
        else:
            return False
