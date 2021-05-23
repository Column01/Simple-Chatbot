# Author: Colin Andress
# Project: Simple Chatbot
# Filename: CommandParser.py
# Purpose: Parses commands from the config file and formats the response.

from Database.SQLiteConnector import SQLiteConnector


def parse_command(_, settings, cmd, data):
    database = SQLiteConnector()
    username = data.username
    user_id = data.userid
    currency = database.get_currency(user_id)
    for i in settings['commands']:
        if i == cmd:
            response = settings['commands'][cmd]['response'].format(username=username, currency=currency, command=cmd)
            return response
        else:
            pass
    else:
        response = f"Unknown command '{cmd}'. Did you type it correctly?"
        return response
