import os
import irc.bot
import requests
import json
from SqliteSearch import SqliteReadDB
import time

configFile = 'config.json'
path = os.path.dirname(__file__)
with open(os.path.join(path, configFile), 'r') as f:
    settings = json.load(f)


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']
        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:' + token)], username, username)

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)
        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            username = e.tags[2]['value']
            print('Received command:', cmd, 'from', username)
            self.do_command(e, cmd)
        # If it is any other chat message, print the username and message to the console
        else:
            # Getting message
            message = e.arguments[0]
            # Getting Username from tags
            username = e.tags[2]['value']
            print(username + ': ' + message)
        return

    def do_command(self, e, cmd):
        c = self.connection
        user_id = e.tags[11]['value']
        username = e.tags[2]['value']

        # Poll the API to get current game.
        if cmd == "game":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' is currently playing ' + r['game'])

        # Poll the API the get the current status of the stream
        elif cmd == "join":
            command_name = 'joincmd'
            currency = 1000
            cooldownmessage = 'You are still on cooldown, ' + username + '. Try again later.'
            addedmessage = username + ' typed !join and was added to the database'
            existingmessage = username + 'Is already in the database. Off cooldown support is not added yet.'
            cooldown = int(time.time()) + 30
            checkcooldown = SqliteReadDB.read_cooldown(user_id, command_name)
            if checkcooldown:
                if checkcooldown:
                    print('User is on cooldown.')
                    c.privmsg(self.channel, cooldownmessage)
            else:
                print('User is off cooldown... trying to add to the database')
                joincommand = SqliteReadDB.add_user(user_id, username, currency, command_name, cooldown)
                if joincommand:
                    print('User added to the database')
                    c.privmsg(self.channel, addedmessage)
                else:
                    print('User is already in the database')
                    c.privmsg(self.channel, existingmessage)

        elif cmd == "coins":
            currency = SqliteReadDB.read_currency(user_id)
            message = 'You have {} coins, {}'.format(currency, username)
            c.privmsg(self.channel, message)

        elif cmd == "title":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' channel title is currently ' + r['status'])

        # Provide basic information to viewers for specific commands
        elif cmd == "discord":
            message = "Join my discord here: https://discord.gg/5J49NNT"
            c.privmsg(self.channel, message)

            # Provide basic information to viewers for specific commands
        elif cmd == "thot":
            message = "BEGONE ... THOT!!!!"
            c.privmsg(self.channel, message)

        elif cmd == "nani":
            message = "Nani the fuck?"
            c.privmsg(self.channel, message)

        elif cmd == "donate":
            message = "You can donate to me at this link: https://streamlabs.com/column01"
            c.privmsg(self.channel, message)

        # The command was not recognized
        else:
            c.privmsg(self.channel, "Unknown Command " + cmd)


def main():
    username = settings['username']
    client_id = settings['client_id']
    token = settings['token']
    channel = settings['channel']
    bot = TwitchBot(username, client_id, token, channel)
    bot.start()


if __name__ == "__main__":
    main()
