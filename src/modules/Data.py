# Author: Colin Andress
# Project: Simple Chatbot
# Filename: data.py
# Purpose: Inits the user information
import modules.SqliteUpdateDB as SqliteUpdateDB

class Data:
    def __init__(self, e):
        self.username = None
        self.userid = None
        self.is_broadcaster = False
        self.is_mod = False

        self.set_information(e)


    def set_information(self, e):
        self.set_username(e)
        self.set_user_id(e)
        self.set_is_broadcaster(e)
        self.set_is_mod(e)


    def set_username(self, e):
        for i in range(len(e.tags)):
            if e.tags[i]['key'] == 'display-name':
                self.username = e.tags[i]['value']
            else:
                pass


    def set_user_id(self, e):
        for i in range(len(e.tags)):
            if e.tags[i]['key'] == 'user-id':
                self.userid = e.tags[i]['value']


    def set_is_broadcaster(self, e):
        for i in range(len(e.tags)):
            if e.tags[i]['key'] == 'badges':
                if e.tags[i]['value'] == 'broadcaster/1':
                    self.is_broadcaster = True
                else:
                    self.is_broadcaster = False


    def set_is_mod(self, e):
        for i in range(len(e.tags)):
            if e.tags[i]['key'] == 'mod':
                if e.tags[i]['value'] == '1':
                    self.is_mod = True
                else:
                    self.is_mod = False


    def check_valid_username(self):
        username_internal = self.username
        user_id_internal = self.userid
        SqliteUpdateDB.update_username(user_id_internal, username_internal)
