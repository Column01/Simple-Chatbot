# Author: Colin Andress
# Project: Simple Chatbot
# Filename: chatbot.py
# Purpose: Main twitch chatbot script. Initializes all functionality of the chatbot

import json
import logging
import os
import sys

import requests
from colored import attr, bg, fg
from irc.bot import SingleServerIRCBot

import modules.CommandParser as CommandParser
from Commands.DebugCommand import DebugCommand
from Commands.DiceGame import DiceGame
from Commands.JoinCommand import JoinCommand
from Commands.SlotsGame import SlotsGame
from Database.SQLiteConnector import SQLiteConnector
from modules.config import ConfigTemplate
from modules.Data import Data
from modules.thread_cleaner import ThreadCleaner

# Load the config file and check if it exists. If it doesn't, generate a template config and quit.
configFile = 'config.json'
path = os.path.dirname(__file__)
try:
    with open(os.path.join(path, configFile), 'r') as f:
        settings = json.load(f)
        f.close()
except FileNotFoundError:
    config = ConfigTemplate()
    config.generate_config()


class TwitchBot(SingleServerIRCBot):
    def __init__(self, username, client_id, token, chan, settings):
        self.reset_color = attr("reset")
        print(fg("#00ff00") + "Thanks for using the chatbot! Use Ctrl+C to exit safely." + self.reset_color)
        self.logger = self.init_logger()
        self.client_id = client_id
        self.token = token
        self.channel = '#' + chan
        self.dice_games = []
        self.settings = settings
        self.database = SQLiteConnector()
        # Get the channel id for v5 API calls if wanted
        url = f'https://api.twitch.tv/helix/users?login={chan}'
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['data'][0]['id']
        # Initialize the thread cleaner
        t_cleaner = ThreadCleaner(self)
        t_cleaner.start()
        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = self.settings["bot_settings"]["port"]
        self.logger.info(f'Connecting to {server} on port {port}')
        SingleServerIRCBot.__init__(self, [(server, port, token)], username, username)

    def on_welcome(self, c, e):
        self.logger.info(f'Joining {self.channel}')
        # Making general requests from twitch so the bot can function
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    # if we get a notice that a message we sent was invalid, print the notice
    def on_pubnotice(self, c, e):
        if e.arguments[0]:
            print(fg("#ff0000") + f"PUBNOTICE FROM TWITCH:{self.reset_color} {e.arguments[0]}")

    # if we get a whisper, treat it like a normal message
    def on_whisper(self, c, e):
        self.on_pubmsg(c, e)

    def on_pubmsg(self, c, e):
        data = Data(e)
        data.check_valid_username()
        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0][1:].split(' ')
            self.do_command(e, cmd)
        # If it is any other chat message, print the username and message to the console
        else:
            message = e.arguments[0]
            username = data.username
            user_color = data.user_color
            print(fg(user_color) + f'[{username}]' + self.reset_color + f': {message}')
            if self.settings["bot_settings"].get("log_chat") is not None:
                if self.settings["bot_settings"]["log_chat"] == 1:
                    self.logger.info(f'CHAT MESSAGE: {username} said {message}')

    def do_command(self, e, cmd):
        data = Data(e)
        if cmd[0] == 'debug':
            debug_command = DebugCommand(data, self.connection, self.channel, self.channel_id, e)
            debug_command.start()
        # if it isn't the debug command, try some other commands.
        else:
            cmd_message = e.arguments[0][1:]
            self.logger.info(f'Recieved Command "{cmd_message}" from {data.username}')
            
            # If the command is the !join command
            if cmd[0] == 'join':
                join_command = JoinCommand(data, self.connection, self.channel, self.settings)
                join_command.start()
                
            # If the command is !slots
            elif cmd[0] == 'slots':
                slots_game = SlotsGame(data, self.connection, self.channel, self.settings)
                slots_game.start()
                
            # If the command is !dice
            elif cmd[0] == 'dice':
                # Make sure we have all arguments for the cmd.
                if len(cmd) >= 2:
                    # If the second argument is "accept" that means its a user accepting a dice battle from another person. 
                    if cmd[1] == "accept":
                        # Forward the event to all dice games and let it parse if the user running it is being waited on.
                        checks_for_player_two = []
                        for game in self.dice_games:
                            test = game.on_pubmsg(data)
                            checks_for_player_two.append(test)
                        # Basically just counts all the returns for the dice game instances and if all elements are false, that means the
                        # user is not being waited on.
                        if checks_for_player_two.count(False) == len(checks_for_player_two):
                            self.connection.privmsg(self.channel, f"You are not being waited on for a dice game, {data.username}. Start a dice game with \"!dice <opponent name> <bet>\"")
                    # If it isn't "accept" we wanna start a new dice battle
                    else:
                        dice_game = DiceGame(data, self.connection, self.channel, self.settings, cmd)
                        dice_game.start()
                        self.dice_games.append(dice_game)
                else:
                    self.connection.privmsg(self.channel, "Sorry, you must be missing something to use the dice command. Use "
                                                          "\"!dice <opponent name> <bet>\" to start a new game.")
            # If the command is anything else, try and parse it from the config file and message the response.
            else:
                tmp = []
                for i in cmd:
                    tmp.append(i + ' ')
                cmd = ''.join(tmp)[:-1]
                response = CommandParser.parse_command(e, settings, cmd, data)
                self.connection.privmsg(self.channel, response)
                
    def init_logger(self):
        logger = logging.getLogger("chatbot")
        handler = logging.FileHandler(filename="chatbot_log.log", encoding="utf-8", mode="a")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        return logger


def main():
    # Load some config settings and start the bot
    username = settings['bot_settings']['username']
    client_id = settings['bot_settings']['client_id']
    token = settings['bot_settings']['token']
    channel = settings['bot_settings']['channel']
    bot = TwitchBot(username, client_id, token, channel, settings)
    bot.start()


if __name__ == '__main__':
    # Try to run the bot. If there is a KeyboardInterrupt at any point, close the script safely.
    try:
        main()
    except KeyboardInterrupt:
        print("Received Keyboard Interrupt, closing chatbot and cleaning up...")
        logger = logging.getLogger("chatbot")
        logger.info("Received Keyboard Interrupt. Closing bot now")
        database = SQLiteConnector()
        database.clear_colors()
        logger.info("Script exiting. See you next time!\n")
        os._exit(0)
