# Author: Colin Andress
# Project: Simple Chatbot
# Filename: CommandParser.py
# Purpose: Parses commands from the config file and formats the response. Called from chatbot.py
import modules.SqliteReadDB as SqliteReadDB


def parse_command(e, settings, cmd, data):
    username = data.username
    user_id = data.userid
    currency = SqliteReadDB.read_currency(user_id)
    for i in settings['commands']:
        if i == cmd:
            response = settings['commands'][cmd]['response'].format(username=username, currency=currency, command=cmd)
            return response
        else:
            pass
    else:
        response = "/w {username} Unknown command '{command}'. " \
                   "Did you type it correctly?".format(username=username, command=cmd)
    return response
