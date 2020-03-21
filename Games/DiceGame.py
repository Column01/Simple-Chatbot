from threading import Thread
from timeit import default_timer as timer
import requests
import random

import modules.SqliteUpdateDB as SqliteUpdateDB

class DiceGame(Thread):

    def __init__(self, data, conn, chan, sett, cmd):
        Thread.__init__(self)
        self.usage = "Use \"!dice <opponent name> <bet>\" to start a game or \"!dice accept\" to accept a battle."
        self.settings = sett
        self.connection = conn
        self.channel = chan
        self.cmd = cmd
        self.waiting_for_accept = True
        self.player_one = data
        if len(cmd) == 3 and int(cmd[2]) > 0:
            self.wager = int(cmd[2])
        else:
            self.wager = -1
        self.player_to_wait_for = cmd[1]
        self.player_two = None
        print(f"Starting a new dice game thread. For {self.player_one.username} versus {self.player_to_wait_for}")

    def run(self):
        self.start_game()
        return

    def start_game(self):
        if self.wager == -1:
            self.send_message(f"You must enter a bet that is more than zero. {self.usage}")
            return
        if self.is_challenging_self():
            self.send_message(f"You cannot dice battle yourself! Please specify another user, you lonely goof. {self.usage}")
            return
        if self.is_player_two_in_chat():
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
            if self.waiting_for_accept == False:
                # Do dice game stuff
                dice_min = self.settings["commands"]["dice"]["min_num"]
                dice_max = self.settings["commands"]["dice"]["max_num"]
                # Rolling the dice
                player_one_roll = random.randint(dice_min, dice_max)
                player_two_roll = random.randint(dice_min, dice_max)
                if player_one_roll == player_two_roll:
                    # Re roll until they are not the same number.
                    while player_one_roll == player_two_roll:
                        player_one_roll = random.randint(dice_min, dice_max)
                        player_two_roll = random.randint(dice_min, dice_max)
                self.send_message(f"Rolling the dice... {self.player_one.username} rolled {player_one_roll} and {self.player_two.username} rolled {player_two_roll}")
                if player_one_roll > player_two_roll:
                    # Player one wins
                    self.send_message(f"Congratulations {self.player_one.username}! You won the battle.")
                    return
                elif player_two_roll > player_one_roll:
                    self.send_message(f"Congratulations {self.player_two.username}! You won the battle.")
                    return
            # This happens when the timer expires on the dice battle.
            elif self.waiting_for_accept == None:
                self.send_message(f"Sorry, {self.player_one.username}. The game timer expired while waiting for {self.player_to_wait_for} to accept the dice battle.")
                return
        else:
            self.send_message(f"Sorry, {self.player_one.username}, that user is not currently in chat. Please try again when they are online next!")
            return

    def is_player_two_in_chat(self):
        # Change URL if you are copying the bot and want to use dice game.
        chan_name = self.settings["bot_settings"]["channel"]
        url = f"https://tmi.twitch.tv/group/user/{chan_name}/chatters"
        req = requests.get(url).json()
        chatters = req["chatters"]
        # This URL returns a JSON object that has the channel's chatters in it. 
        # We get the ["chatters"] which has sub keys that have a list of viewers that fit each one (broadcaster, mod, viewer, etc).
        # This just loops over all of those sub keys and checks if the user is present.
        for key in chatters:
            user_category = chatters[key]
            for user in user_category:
                if user == self.player_to_wait_for:
                    return True
        return False

    """Checks whether the user is challenging themself to a dice battle.
    
    Returns:
        Boolean -- Whether or not they challenged themselves
    """    
    def is_challenging_self(self):
        return self.player_one.username.lower() == self.player_to_wait_for.lower()
    
    def send_message(self, msg):
        self.connection.privmsg(self.channel, msg)
    
    """pubmsg event for each dice game.
    Returns:
        Boolean -- Returns whether or not the player was the one we were waiting for in this dice game.
    """    
    def on_pubmsg(self, data):
        if data.username.lower() == self.player_to_wait_for.lower():
            self.player_two = data
            self.waiting_for_accept = False
            return True
        else:
            return False
