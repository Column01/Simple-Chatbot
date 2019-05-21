# Author: Colin Andress
# Project: Simple Chatbot
# Filename: dice.py
# Purpose: The dice battle game for my chatbot.
import random
import modules.SqliteReadDB as SqliteReadDB
import modules.SqliteUpdateDB as SqliteUpdateDB
import modules.Data as Data


def dice_game(e, settings, cmd):
    game = cmd[0]
    username = Data.username(e)
    user_id = Data.user_id(e)
    cooldown = settings['commands']['dice']['cooldown']
    minnum = settings['commands']['dice']['min_num']
    maxnum = settings['commands']['dice']['max_num']
    multiplier = settings['commands']['dice']['multiplier']
    if cmd[1] and cmd[2]:
        try:
            guess = int(cmd[1])
            bet = int(cmd[2])
            if guess > maxnum:
                response = "I'm sorry {username}, but {guess} is bigger than the max number of {maxnum}. " \
                           "Please try again!".format(username=username, guess=guess, maxnum=maxnum)
                return response
            # Checking user cooldown...
            user_cooldown = SqliteReadDB.read_cooldown(user_id, game)
            # If the cooldown check returns that they are off cooldown
            if user_cooldown is False:
                # Removes the cost from their currency, starts the dice roll and put the user to a cooldown
                cost_removal = SqliteUpdateDB.cost_subtract(user_id, bet)
                if cost_removal:
                    SqliteUpdateDB.add_cooldown(user_id, game, cooldown)
                    roll = random.randint(minnum, maxnum)
                    if roll == guess:
                        reward = bet * multiplier
                        SqliteUpdateDB.add_currency(user_id, reward)
                        response = settings['commands']['dice']['success_message'].format(username=username,
                                                                                          number=roll, guess=guess,
                                                                                          reward=reward)
                        return response
                    else:
                        response = settings['commands']['dice']['wrong_number'].format(username=username,
                                                                                       number=roll, guess=guess)
                        return response
                else:
                    response = "I'm sorry {username}, but you do not have enough currency for a bet of {bet} coins." \
                        .format(username=username, bet=bet)
                    return response
            # If the cooldown check returns a number, return that they are on cooldown and the duration of the cooldown
            elif isinstance(user_cooldown, int):
                return user_cooldown
        except ValueError as e:
            print(e)
            response = 'Sorry {username}, your guess and bet need to be numbers.'.format(username=username)
            return response

    elif not cmd[1]:
        response = 'You need to provide a bet, {username}. Format: !dice <guess> <bet>'.format(username=username)
        return response
    elif not cmd[2]:
        response = 'You need to provide a guess, {username}. Format: !dice <guess> <bet>'.format(username=username)
        return response
    else:
        response = 'You need to provide a guess and a bet, {username}. Format: !dice <guess> <bet>'.format(username=username)
        return response
