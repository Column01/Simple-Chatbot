from threading import Thread
from timeit import default_timer as timer
import requests
import random

import modules.SqliteUpdateDB as SqliteUpdateDB

class DiceGame(Thread):

    def __init__(self, data, conn, chan, sett, cmd):
        Thread.__init__(self)
        self.settings = sett
        self.connection = conn
        self.channel = chan
        self.cmd = cmd
        self.waiting_for_accept = True
        self.player_one = data
        if cmd[2] > 0:
            self.wager = cmd[2]
        self.player_to_wait_for = cmd[1]
        self.player_two = None

    def run(self):
        self.start_game()
        return

    def start_game(self):
        if self.is_player_two_in_chat():
            self.connection.privmsg(self.channel, f"Hey @{self.player_to_wait_for}! "
                                                f"{self.player_one.username} has challenged you to a dice battle for {self.wager} coins.\n"
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
                dice_min = settings["commands"]["dice"]["min_num"]
                dice_max = settings["commands"]["dice"]["max_num"]
                # Rolling the dice
                player_one_roll = random.randint(dice_min, dice_max)
                player_two_roll = random.randint(dice_min, dice_max)
                if player_one_roll == player_two_roll:
                    # Re roll until they are not the same number.
                    while player_one_roll == player_two_roll:
                        player_one_roll = random.randint(dice_min, dice_max)
                        player_two_roll = random.randint(dice_min, dice_max)
                if player_one_roll > player_two_roll:
                    # Player one wins
                    pass
                elif player_two_roll > player_one_roll:
                    # Player two wins
                    pass

            # This happens when the timer expires on the dice battle.
            elif self.waiting_for_accept == None:
                self.connection.privmsg(self.channel, f"Sorry, {self.player_one.username}. The game timer expired while waiting for {self.player_two.username} to accept the dice battle.")
                return
        else:
            self.connection.privmsg(self.channel, f"Sorry, {self.player_one.username}, that user is not currently in chat. Please try again when they are online next!")
            return

    def is_player_two_in_chat(self):
        # Change URL if you are copying the bot and want to use dice game.
        chan_name = self.settings["channel"]
        url = f"https://tmi.twitch.tv/group/user/{chan_name}/chatters"
        req = requests.get(url)
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

    '''pubmsg event for each dice game. Returns a boolean if the user is the player we were looking for or not.
    Used to continue once the user who is being waited on for this dice game instance accepts the duel.
    '''
    def on_pubmsg(self, data):
        if data.username == self.player_to_wait_for:
            self.player_two = data
            self.waiting_for_accept = False
            return True
        else:
            return False
    