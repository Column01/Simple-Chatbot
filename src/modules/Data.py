# Author: Colin Andress
# Project: Simple Chatbot
# Filename: Data.py
# Purpose: Returns user data when passed the tags. Also has some misc functions.
import modules.SqliteUpdateDB as SqliteUpdateDB


def username(e):
    for i in range(len(e.tags)):
        if e.tags[i]['key'] == 'display-name':
            username = e.tags[i]['value']
            return username
        else:
            pass


def user_id(e):
    for i in range(len(e.tags)):
        if e.tags[i]['key'] == 'user-id':
            user_id = e.tags[i]['value']
            return user_id
        else:
            pass


def is_broadcaster(e):
    for i in range(len(e.tags)):
        if e.tags[i]['key'] == 'badges':
            if e.tags[i]['value'] == 'broadcaster/1':
                return True
            else:
                return False
        else:
            pass


def is_mod(e):
    for i in range(len(e.tags)):
        if e.tags[i]['key'] == 'mod':
            if e.tags[i]['value'] == '1':
                return True
            else:
                return False
        else:
            pass


def yeet(exception):
    raise exception


def check_valid_username(e):
    username_internal = username(e)
    user_id_internal = user_id(e)
    SqliteUpdateDB.update_username(user_id_internal, username_internal)
