# Simple Chatbot
A chatbot written in Python for Twitch chat. Keep your viewers engaged with an interactive chatbot where they can earn currency and gamble for fun! Make fun little command responses that are unique to you!

## Dependencies
- [Python 3.4+](https://www.python.org/downloads/)
- [Requests Library](https://pypi.org/project/requests/)
- [IRC Library](https://pypi.org/project/irc/)

(Command to get dependencies: `pip install requests irc`)

## Setup
First off you need to run the main script to generate a template config so you can fill in the info needed (see **"How to Run"** below). You will need your own bot account and you will need to [register it as a twitch application](https://dev.twitch.tv/console). Once registered, you can get the client ID there and add it in the config file. Then you need to generate an OAuth token using [this tool](https://twitchapps.com/tmi/) while logged into the bot account (**NOT** the streamer account).

Now you can edit the chatbot commands in the config to include responses and appropriate links you want (if you don't, it will send my donation link and my discord invite if people use those commands). To add commands, just add a new command object in the config file identical to the others, name it the command you want to run (So if you added "test" the command in chat would be !test) and change the response.

- Currently supported placeholders for basic text response commands:
	- `{username}`, `{command}`, `{currency}`
- Currently support game response placeholders:
	- `{username}`, `{command}`, `{reward}` and for cooldown remainders: `{minutes}` , `{seconds}`

## How to Run
- Add them directly to your system site packages or Create a virtualenv with the dependencies fulfilled and then activate that venv.
- Run the chatbot `python chatbot.py`

## Donations
Donations help me stay motivated and working on projects like these. If you feel led to donate, please click the link [here](https://www.paypal.me/column01). Any amount is appreciated but is not necessary to enjoy this program.

## Todo
- Add a dice game

## Contributors
- Column01 (Dev)
