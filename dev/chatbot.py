import os
import irc.bot
import requests
import json
try:
    from src import commandParser
except ImportError:
    try:
        from dev import commandParser
    except ImportError:
        import commandParser
try:
    from SqliteSearch import SqliteReadDB, SqliteUpdateDB
except ImportError:
    import SqliteReadDB, SqliteUpdateDB

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
            self.do_command(e, cmd)
        # If it is any other chat message, print the username and message to the console
        else:
            # Getting message
            message = e.arguments[0]
            # Getting Username from tags
            username = e.tags[3]['value']
            print(username + ': ' + message)
        return

    def do_command(self, e, cmd):
        c = self.connection
        user_id = e.tags[12]['value']
        username = e.tags[3]['value']

        usernamedb = SqliteReadDB.read_username(user_id)
        if usernamedb is None:
            print('Adding ' + username + ' to database...')
            SqliteUpdateDB.add_user(user_id, username, 0, 0, 0)
        elif username == usernamedb[0]:
            pass
        elif username != usernamedb[0]:
                print(username + ' has mismatched usernames. Updating.')
                SqliteUpdateDB.update_username(user_id)

        if cmd == 'debug':
            print('Recieved Debug command from ' + username + '. Printing user tags...')
            print(e.tags)
            print('\n')
        else:
            print('Received command:', cmd, 'from', username)

            if cmd == 'join':
                game = cmd
                currency = settings['bot_settings']['join_reward']
                cooldown = settings['bot_settings']['join_cooldown']
                joinmessage = settings['bot_settings']['join_message'].format(username, cmd, currency)
                checkcooldown = SqliteReadDB.read_cooldown(user_id, game)
                if checkcooldown is False:
                    print(username + ' is off cooldown... trying to update database')
                    SqliteUpdateDB.add_currency(user_id, currency)
                    SqliteUpdateDB.add_cooldown(user_id, game, cooldown)
                    c.privmsg(self.channel, joinmessage)
                elif isinstance(checkcooldown, int):
                    print('User is on cooldown.')
                    cooldownmessage = settings['bot_settings']['cooldown_message'].format(username, checkcooldown)
                    c.privmsg(self.channel, cooldownmessage)
            else:
                response = commandParser.response_format(e, settings, cmd)
                c.privmsg(self.channel, response)


def main():
    username = settings['bot_settings']['username']
    client_id = settings['bot_settings']['client_id']
    token = settings['bot_settings']['token']
    channel = settings['bot_settings']['channel']
    bot = TwitchBot(username, client_id, token, channel)
    bot.start()


if __name__ == '__main__':
    main()
