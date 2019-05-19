# Author: Colin Andress
# Project: Simple Chatbot
# Filename: config.py
# Purpose: Generates a template config. Called from chatbot.py when no config exists and exits upon completion
import json

# Config Template
template = '{"bot_settings":{"username":"Bot Username","host":"irc.chat.twitch.tv","port":6667,"token":"Oauth token","channel":"twitch streamer username","client_id":"client_ID of bot account","poll_rate":600},"commands":{"coins":{"response":"{username} has {currency} coins to spend, Go play some games :P"},"discord":{"response":"Join my discord here: https://discord.gg/5J49NNT Kappa"},"nani":{"response":"Nani the fuck?"},"thot":{"response":"Begone ... THOT!!!!"},"donate":{"response":"You can donate to me at this link: https://streamlabs.com/column01"},"join":{"cooldown_message":"/w {username} You are still on cooldown for {minutes} minutes and {seconds} seconds, {username}. Try again later.","success_message":"{username} typed !{command} and recieved {reward} coins.","join_reward":5000,"join_cooldown":3600},"slots":{"cooldown_message":"/w {username} You are still on cooldown for {minutes} minutes and {seconds} seconds, {username}. Try again later.","cooldown":300,"double_reward":2000,"triple_reward":10000,"jackpot_reward":25000,"cost":100,"reel":["Kappa","PogChamp","LUL","BlessRNG","KappaPride","DoritosChip","TheIlluminati"]}}}'


def yeet(exception):
    raise exception


# Generates the config file from the template.
def generate_config():
    config_file = json.loads(template)
    with open('config.json', 'w+') as s:
        json.dump(config_file, s, indent=4, sort_keys=True)
    print("Config file was not found. Generated template config and will exit the chatbot. "
          "\nEditing of the file is required to use the bot so please see the readme for instructions.")
    yeet(SystemExit)
