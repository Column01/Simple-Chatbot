# Author: Colin Andress
# Project: Simple Chatbot
# Filename: commandParser.py
# Purpose: Parses commands from the config file and formats the response. Called from chatbot.py
import modules.SqliteReadDB as SqliteReadDB


def parse_command(e, settings, cmd):
    username = e.tags[3]['value']
    user_id = e.tags[12]['value']
    currency = SqliteReadDB.read_currency(user_id)
    for i in settings['commands']:
        if i == cmd:
            response = settings['commands'][cmd]['response'].format(username=username, currency=currency, command=cmd)
            return response
        else:
            pass
    else:
        response = "/w {username} Unknown command '{cmd}'. " \
                   "Did you type it correctly?".format(username=username, cmd=cmd)
    return response
