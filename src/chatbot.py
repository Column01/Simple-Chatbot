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
import modules.commandParser as commandParser
import modules.slots as slots
import modules.config as config


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
    def __init__(self, username, client_id, token, channel):
        print('Thanks for using the chatbot! Use Ctrl+C to exit safely.')
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        # Get the channel id for v5 API calls if wanted
        url = 'https://api.twitch.tv/kraken/users?login={channel}'.format(channel=channel)
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']
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

    def on_pubmsg(self, c, e):
        Data.check_valid_username(e)
        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            self.do_command(e, cmd)
        # If it is any other chat message, print the username and message to the console
        else:
            # Getting message
            message = e.arguments[0]
            # Getting Username from tags
            username = Data.username(e)
            print('{username}: {message}'.format(username=username, message=message))
        return

    def do_command(self, e, cmd):
        c = self.connection
        # Command sender's username and user_id are grabbed from the tags
        user_id = Data.user_id(e)
        username = Data.username(e)
        if cmd == 'debug':
            # If the debug command sender is the broadcaster or a channel mod
            if Data.is_broadcaster(e) or Data.is_mod(e):
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
            print('Received command: {cmd} from {username}'.format(cmd=cmd, username=username))
            # If the command is the !join command
            if cmd == 'join':
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
                    cooldown = divmod(checkcooldown, 60)
                    cooldownmessage = settings['commands'][cmd]['cooldown_message'].format(username=username,
                                                                                           minutes=cooldown[0],
                                                                                           seconds=cooldown[1])
                    c.privmsg(self.channel, cooldownmessage)
            # If the command is !slots
            elif cmd == 'slots':
                # Execute the slots
                result = slots.slots_execute(e, settings, cmd)
                # if the result is a number, they are on cooldown so reply with the cooldown message
                if isinstance(result, int):
                    cooldown = divmod(result, 60)
                    message = settings['commands'][cmd]['cooldown_message'].format(username=username,
                                                                                   minutes=cooldown[0],
                                                                                   seconds=cooldown[1])
                    c.privmsg(self.channel, message)
                # If the result has 2 items, that means it was successful. Print the roll and the result
                elif len(result) == 2:
                    message = result[0] + result[1]
                    c.privmsg(self.channel, message)
                # Ff all else fails and only one result comes back, they don't have enough money to use the slots.
                else:
                    message = result
                    c.privmsg(self.channel, message)
            # If the command is anything else, try and parse it from the config file and message the response.
            else:
                response = commandParser.parse_command(e, settings, cmd)
                c.privmsg(self.channel, response)


# Data class. Call any function and pass it the tags (e) and it will return whatever the function is named.
class Data:
    @staticmethod
    def username(e):
        for i in range(len(e.tags)):
            if e.tags[i]['key'] == 'display-name':
                username = e.tags[i]['value']
                return username
            else:
                pass

    @staticmethod
    def user_id(e):
        for i in range(len(e.tags)):
            if e.tags[i]['key'] == 'user-id':
                user_id = e.tags[i]['value']
                return user_id
            else:
                pass

    @staticmethod
    def is_broadcaster(e):
        for i in range(len(e.tags)):
            if e.tags[i]['key'] == 'badges':
                if e.tags[i]['value'] == 'broadcaster/1':
                    return True
                else:
                    return False
            else:
                pass

    @staticmethod
    def is_mod(e):
        for i in range(len(e.tags)):
            if e.tags[i]['key'] == 'mod':
                if e.tags[i]['value'] == '1':
                    return True
                else:
                    return False
            else:
                pass

    @staticmethod
    def check_valid_username(e):
        username = Data.username(e)
        user_id = Data.user_id(e)
        SqliteUpdateDB.update_username(user_id, username)


def main():
    # Load some config settings and start the bot
    username = settings['bot_settings']['username']
    client_id = settings['bot_settings']['client_id']
    token = settings['bot_settings']['token']
    channel = settings['bot_settings']['channel']
    bot = TwitchBot(username, client_id, token, channel)
    bot.start()


if __name__ == '__main__':
    # Try to run the bot. If there is a KeyboardInterrupt at any point, close the script safely.
    try:
        main()
    except KeyboardInterrupt:
        print("Recieved Keyboard Interrupt, closing chatbot and cleaning up...")
        raise SystemExit
