# Author: Colin Andress
# Project: Simple Chatbot
# Filename: CommandParser.py
# Purpose: Parses commands from the config file and formats the response.

from Database.SQLiteConnector import SQLiteConnector


def parse_command(_, settings, cmd, data):
    database = SQLiteConnector()
    currency = database.get_currency(data.userid)
    command = settings["commands"].get(cmd)
    if command is None:
        return f"Unknown command '{cmd}'. Did you type it correctly?"
    else:
        return command["response"].format(username=data.username, currency=currency, command=cmd)
