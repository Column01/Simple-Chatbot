import random
import modules.SqliteReadDB as SqliteReadDB
import modules.SqliteUpdateDB as SqliteUpdateDB


def slots_execute(e, settings, cmd):
    # Variables galore!
    username = e.tags[3]['value']
    userid = e.tags[12]['value']
    cost = settings["commands"][cmd]["cost"]
    cooldown = settings["commands"][cmd]["cooldown"]
    reel = settings["commands"][cmd]["reel"]
    jackpot = settings["commands"][cmd]["jackpot_reward"]
    triple = settings["commands"][cmd]["triple_reward"]
    double = settings["commands"][cmd]["double_reward"]
    # Checking user cooldown...
    user_cooldown = SqliteReadDB.read_cooldown(userid, cmd)
    # If the cooldown check returns that they are off cooldown
    if user_cooldown is False:
        # Removes the cost from their currency, starts the slots roll and puts the user to a cooldown
        cost_removal = SqliteUpdateDB.cost_subtract(userid, cost)
        if cost_removal:
            SqliteUpdateDB.add_cooldown(userid, cmd, cooldown)
            slots = slots_roll(reel)
            roll = '{} typed !slots and rolled for {} coins... {} ... {} ... {} ... '.format(username, cost, slots[0], slots[1], slots[2])
            # If it's a Jackpot
            if all(x == slots[0] for x in slots) and slots[0] == "KappaPride":
                SqliteUpdateDB.add_currency(userid, jackpot)
                message = '{} has hit the jackpot! You win {} coins!'.format(username, jackpot)
                return roll, message
            # If it's a Triple
            elif all(x == slots[0] for x in slots) and slots[0] != "KappaPride":
                SqliteUpdateDB.add_currency(userid, triple)
                message = '{} has gotten 3 of the same emote and won {} coins!'.format(username, triple)
                return roll, message
            # If it's a Double 1 2
            elif slots[0] == slots[1] and slots[1] != slots[2]:
                SqliteUpdateDB.add_currency(userid, double)
                message = '{} has gotten 2 of the same emote and won {} coins!'.format(username, double)
                return roll, message
            # If it's a Double 2 3
            elif slots[1] == slots[2] and slots[1] != slots[0]:
                SqliteUpdateDB.add_currency(userid, double)
                message = '{} has gotten 2 of the same emote and won {} coins!'.format(username, double)
                return roll, message
            # If it's a Double 3 1
            elif slots[0] == slots[2] and slots[0] != slots[1]:
                SqliteUpdateDB.add_currency(userid, double)
                message = '{} has gotten 2 of the same emote and won {} coins!'.format(username, double)
                return roll, message
            # If it's a Loss
            elif slots[0] != slots[1] and slots[0] != slots[2] and slots[2] != slots[1]:
                message = "I'm sorry, {}, but you lost!".format(username)
                return roll, message
        else:
            message = "You have insufficient currency, {}. The slots requires 100 coins Run !coins to see " \
                      "your balance. You can also run !join to gain some to kick start your earning!".format(username)
            return message
    # If the cooldown check returns a number, return that they are on cooldown and the duration of the cooldown
    elif isinstance(user_cooldown, int):
        return user_cooldown


def slots_roll(reel):
    slots_result = []
    for i in range(3):
        # Picks a random choice from the reel and appends it to an array
        slot = random.choice(reel)
        slots_result.append(slot)
    return slots_result
