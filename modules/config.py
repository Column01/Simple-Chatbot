# Author: Colin Andress
# Project: Simple Chatbot
# Filename: config.py
# Purpose: Generates a template config. Called when no config exists and exits upon completion

import json


class ConfigTemplate:

    def __init__(self):
        self.template = {
            "bot_settings": {
                "username": "Bot account username",
                "host": "irc.chat.twitch.tv",
                "port": 6667,
                "token": "Bot oauth token",
                "channel": "Streamer name",
                "client_id": "Client ID of bot account",
                "log_chat": False
            },
            "commands": {
                "coins": {
                    "response": "{username} has {currency} coins to spend, Go play some games :P"
                },
                "discord": {
                    "response": "Join my discord here: https://discord.gg/5J49NNT Kappa"
                },
                "nani": {
                    "response": "Nani the fuck?"
                },
                "thot": {
                    "response": "Begone ... THOT!!!!"
                },
                "donate": {
                    "response": "You can donate to me at this link: https://streamlabs.com/column01"
                },
                "join": {
                    "cooldown_message": "You are still on cooldown for {minutes} minutes and {seconds} seconds, {username}. Try again later.",
                    "success_message": "{username} typed !{command} and recieved {reward} coins.",
                    "join_reward": 5000,
                    "join_cooldown": 3600
                },
                "slots": {
                    "cooldown_message": "You are still on cooldown for {minutes} minutes and {seconds} seconds, {username}. Try again later.",
                    "cooldown": 600,
                    "double_reward": 2000,
                    "triple_reward": 10000,
                    "jackpot_reward": 25000,
                    "cost": 100,
                    "reel": [
                        "Kappa",
                        "PogChamp",
                        "LUL",
                        "BlessRNG",
                        "KappaPride",
                        "DoritosChip",
                        "TheIlluminati"
                    ]
                },
                "dice": {
                    "min_num": 1,
                    "max_num": 6,
                    "cooldown": 300
                }
            }
        }

    # Generates the config file from the template.
    def generate_config(self):
        with open('config.json', 'w+') as s:
            json.dump(self.template, s, indent=4)
        print("Config file was not found. Generated template config and will exit the chatbot. "
              "\nEditing of the file is required to use the bot so please see the readme for instructions.")
        exit(0)
