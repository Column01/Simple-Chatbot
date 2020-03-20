# Author: Colin Andress
# Project: Simple Chatbot
# Filename: dice.py
# Purpose: The dice game. Command Format: !dice <guess> <bet>
import random
import modules.SqliteReadDB as SqliteReadDB
import modules.SqliteUpdateDB as SqliteUpdateDB
import modules.helpers as helpers


def dice_game(e, settings, cmd, data):
    game = cmd[0]
    username = data.username
    user_id = data.userid
    cooldown = settings['commands']['dice']['cooldown']
    minnum = settings['commands']['dice']['min_num']
    maxnum = settings['commands']['dice']['max_num']
    multiplier = settings['commands']['dice']['multiplier']
    if len(cmd) == 3:
        # check again that both arguments are set
        if cmd[1] and cmd[2]:
            # Then try to convert the guess and bet to integers and run the rest of the script.
            try:
                guess = int(cmd[1])
                bet = int(cmd[2])
                # if their guess is higher than the max number, cancel running and tell them.
                if guess > maxnum:
                    response = "I'm sorry {username}, but {guess} is bigger than the max number of {maxnum}. " \
                            "Please try again!".format(username=username, guess=guess, maxnum=maxnum)
                    return response
                # Checking user cooldown...
                user_cooldown = SqliteReadDB.read_cooldown(user_id, game)
                # If the cooldown check returns that they are off cooldown
                if user_cooldown is False:
                    # Removes the cost from their currency, starts the dice roll and put the user on cooldown
                    cost_removal = SqliteUpdateDB.cost_subtract(user_id, bet)
                    if cost_removal:
                        SqliteUpdateDB.add_cooldown(user_id, game, cooldown)
                        roll = random.randint(minnum, maxnum)
                        # if the guess was right, reward them and send the success message
                        if roll == guess:
                            reward = bet * multiplier
                            SqliteUpdateDB.add_currency(user_id, reward)
                            response = settings['commands']['dice']['success_message'].format(username=username,
                                                                                            number=roll, guess=guess,
                                                                                            reward=reward)
                            return response
                        # if the guess was wrong, send the failure message
                        else:
                            response = settings['commands']['dice']['wrong_number'].format(username=username,
                                                                                        number=roll, guess=guess)
                            return response
                    # if it couldn't take the cost off their currency, tell them they don't have enough coins.
                    else:
                        response = "I'm sorry {username}, but you do not have enough currency for a bet of {bet} coins." \
                            .format(username=username, bet=bet)
                        return response
                # If the cooldown check returns a number, return that they are on cooldown and the duration of the cooldown
                elif isinstance(user_cooldown, int):
                    return user_cooldown
            # If it fails to convert the guess or bet to a number, tell them they need to be numbers.
            except ValueError as e:
                print(e)
                response = 'Sorry {username}, your guess and bet need to be numbers. Format: !dice <guess> <bet>'\
                    .format(username=username)
                return response
    else:
         # if the guess is not set tell them to provide a guess
        if not helpers.test_list_item(cmd, 1):
            response = 'You need to provide a guess, {username}. Format: !dice <guess> <bet>'.format(username=username)
        # if the bet is not set tell them to provide a bet
        elif not helpers.test_list_item(cmd, 2):
            response = 'You need to provide a bet, {username}. Format: !dice <guess> <bet>'.format(username=username)
        else:
            response = 'You need to provide a guess and a bet, {username}. Format: !dice <guess> <bet>'.format(username=username)
        return response
