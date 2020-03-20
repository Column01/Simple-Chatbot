# Author: Colin Andress
# Project: Simple Chatbot
# Filename: chatbot.py
# Purpose: Main twitch chatbot script.
import os
import irc.bot
import requests
import json
import modules.SqliteReadDB as SqliteReadDB
import modules.SqliteUpdateDB as SqliteUpdateDB
import modules.CommandParser as CommandParser
import modules.config as config
import modules.slots as slots
from modules.Data import Data

from Games.DiceGame import DiceGame


# Load the config file and check if it exists. If it doesn't, generate a template config and quit.
configFile = 'config.json'
path = os.path.dirname(__file__)
try:
    with open(os.path.join(path, configFile), 'r') as f:
        settings = json.load(f)
        f.close()
except FileNotFoundError:
    config.generate_config()


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel, settings):
        print('Thanks for using the chatbot! Use Ctrl+C to exit safely.')
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.data = None
        self.dice_games = []
        self.settings = settings
        # Get the channel id for v5 API calls if wanted
        url = 'https://api.twitch.tv/helix/users?login={channel}'.format(channel=channel)
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['data'][0]['id']
        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to {server} on port {port}...'.format(server=server, port=port))
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, token)], username, username)

    def on_welcome(self, c, e):
        print('Joining {channel}'.format(channel=self.channel))
        # Making general requests from twitch so the bot can function
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    # if we get a notice that a message we sent was invalid, print the notice
    def on_pubnotice(self, c, e):
        if e.arguments[0]:
            print(e.arguments[0])

    # if we get a whisper, treat it like a normal message
    def on_whisper(self, c, e):
        self.on_pubmsg(c, e)

    def on_pubmsg(self, c, e):
        self.data = Data(e)
        self.data.check_valid_username()
        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0][1:].split(' ')
            self.do_command(e, cmd)
        # If it is any other chat message, print the username and message to the console
        else:
            message = e.arguments[0]
            username = self.data.username
            print('{username}: {message}'.format(username=username, message=message))
        return

    def do_command(self, e, cmd):
        c = self.connection
        user_id = self.data.userid
        username = self.data.username
        if cmd[0] == 'debug':
            # If the debug command sender is the broadcaster or a channel mod
            if self.data.is_broadcaster or self.data.is_mod:
                print('Recieved Debug command from {username}... Printing tags'.format(username=username))
                c.privmsg(self.channel, "/w {username} Printed tags to the console of the chatbot. "
                                        "I hope you were asked to run this "
                                        "or you wanted to debug something".format(username=username))
                print("User Tags:\n{tags}\n"
                      "Recieved Message: {message}\n"
                      "Connected Channel: {channel}\n"
                      "Channel ID: {channelid}\n"
                      "".format(channel=self.channel, channelid=self.channel_id, tags=e.tags, message=e.arguments[0]))
            else:
                c.privmsg(self.channel, "/w {username} You are not authorized to use the debug command, {username}. "
                                        "Please ask the streamer for permission if you believe this is "
                                        "an error.".format(username=username))
        # if it isn't the debug command, try some other commands.
        else:
            cmdmessage = e.arguments[0][1:]
            print('Recieved Command "{cmd}" from {username}'.format(cmd=cmdmessage, username=username))
            # If the command is the !join command
            if cmd[0] == 'join':
                cmd = cmd[0]
                game = cmd
                # Check cooldown and load necessary settings
                currency = settings['commands']['join']['join_reward']
                cooldown = settings['commands']['join']['join_cooldown']
                checkcooldown = SqliteReadDB.read_cooldown(user_id, game)
                # If they are off cooldown, let the command execute as planned
                if checkcooldown is False:
                    SqliteUpdateDB.add_currency(user_id, currency)
                    SqliteUpdateDB.add_cooldown(user_id, game, cooldown)
                    reward = settings['commands']['join']['join_reward']
                    joinmessage = settings['commands'][cmd]['success_message'].format(username=username, reward=reward,
                                                                                      command=cmd)
                    c.privmsg(self.channel, joinmessage)
                # If the cooldown comes back as a number (in seconds)
                elif isinstance(checkcooldown, int):
                    # Convert it to minutes and seconds and message the user using the cooldown message from the config
                    minutes, seconds = divmod(checkcooldown, 60)
                    cooldownmessage = settings['commands'][cmd]['cooldown_message'].format(username=username,
                                                                                           minutes=minutes,
                                                                                           seconds=seconds)
                    c.privmsg(self.channel, cooldownmessage)
            # If the command is !slots
            elif cmd[0] == 'slots':
                cmd = cmd[0]
                # Execute the slots
                result = slots.slots_execute(e, settings, cmd, self.data)
                print(result)
                print(isinstance(result, int))
                # if the result is a number, they are on cooldown so reply with the cooldown message
                if isinstance(result, int):
                    minutes, seconds = divmod(result, 60)
                    message = settings['commands'][cmd]['cooldown_message'].format(username=username,
                                                                                   minutes=minutes,
                                                                                   seconds=seconds)
                    c.privmsg(self.channel, message)
                # If the result has 2 items, that means it was successful. Print the roll and the result
                elif len(result) == 2:
                    message = result[0] + result[1]
                    c.privmsg(self.channel, message)
                # If all else fails and only one result comes back, they don't have enough money to use the slots.
                else:
                    message = result
                    c.privmsg(self.channel, message)

            # If the command is !dice
            elif cmd[0] == 'dice':
                # Make sure we have all arguments for the cmd.
                if len(cmd) == 3:
                    # If the second argument is "accept" that means its a user accepting a dice battle from another person. 
                    if cmd[1] == "accept":
                        # Forward the event to all dice games and let it parse if the user running it is being waited on.
                        checks_for_player_two = []
                        for game in self.dice_games:
                            test = game.on_pubmsg(self.data)
                            checks_for_player_two.append(test)
                        # Basically just counts all the returns for the dice game instances and if all elements are false, that means the
                        # user is not being waited on.
                        if checks_for_player_two.count(False) == len(checks_for_player_two):
                            self.connection.privmsg(self.channel, f"You are not being waited on for a dice game, {self.data.username}. Start a dice game with \"!dice <opponent name> <bet>\"")
                    # If it isn't "accept" we wanna start a new dice battle
                    else:
                        dice_game = DiceGame(self.data, self.connection, self.channel, self.settings, cmd)
                        dice_game.run()
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
                response = CommandParser.parse_command(e, settings, cmd, self.data)
                c.privmsg(self.channel, response)


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
        exit(0)
