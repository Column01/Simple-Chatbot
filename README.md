# A Simple Chatbot for Twitch IRC
Just a simple chatbot for IRC.

## Dependencies
- [Python 3.4+](https://www.python.org/downloads/)
- [Requests Library](https://pypi.org/project/requests/) for python
- [IRC Library](https://pypi.org/project/irc/) for Python
- Command to get dependencies: `pip install requests irc`

## How to run:

Fill in the info needed inside the `config.json` file. You will need your own bot account and to register it as a twitch application. If you don't know how to get one of the items needed, a quick google search should help you.

Edit the chatbot config to include the command responses and appropriate links you want (if you don't, it will send my donation link and my discord invite if people use those commands). To add commands, just add a new command object in the config file identical to the others and change the data to the name (the name is what triggers it in chat. So if you added "test" the command in chat would be !test) and the response you want for it.

- Currently supported placeholders for basic text response commands:
	- `{username}`, `{command}`, `{currency}`, `{cooldown}`
- Currently support game response placeholders:
	- `{username}`, `{command}`, `{reward}`, `{cooldown}`

### Setup
- Create a venv with the dependencies above fulfilled and activate that venv
- `python .\chatbot.py`

## Donations
Donations help me stay motivated and working on projects like these. If you feel led to donate, please click the link [here](https://www.paypal.me/column01). Any amount is appreciated but is not necessary to enjoy this program.

## To do
- Add a dice game

## Credits
- Column01 (Dev)
