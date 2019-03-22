# A Simple Chatbot for Twitch IRC
Just a simple chatbot for IRC.

## Dependencies
- [Python 3.4+](https://www.python.org/downloads/)
- [Requests Library](https://pypi.org/project/requests/) for python
- [IRC Library](https://pypi.org/project/irc/) for Python
- `pip install requests irc`

## How to run:

Fill in the info needed inside the `config.json` file. You will need your own bot account and to register it as a twitch application. If you don't know how to get one of the items needed, a quick google search should help you.

Edit the chatbot script to include the command responses you want (if you don't, it will send my donation link and my discord invite if people use those commands)

- Create a venv with the dependencies above fufilled
- `python chatbot.py`

## Donations
Donations help me stay motivated and working on projects like these. If you feel led to donate, please click the link [here](https://www.paypal.me/column01). Any amount is apprieciated but is not nessecary to enjoy this program.

## Plans
- Refine Join command
- Refine cooldown system
- Slots game
- Add a dice game
- Easy command additions from config

## Credits
- Column01 (Dev)
