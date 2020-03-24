# Author: Colin Andress
# Project: Simple Chatbot
# Filename: data.py
# Purpose: Inits the user information
from Database.SQLiteConnector import SQLiteConnector

class Data:
    
    def __init__(self, e):
        self.username = None
        self.userid = None
        self.is_broadcaster = False
        self.is_mod = False
        self.user_color = None
        
        self.set_information(e)

    def set_information(self, e):
        for i in range(len(e.tags)):
            # Set their username
            if e.tags[i]['key'] == 'display-name':
                self.username = e.tags[i]['value']
                
            # Set their userid
            elif e.tags[i]['key'] == 'user-id':
                self.userid = e.tags[i]['value']
                
            # Set their user color
            elif e.tags[i]['key'] == "color":
                self.user_color = e.tags[i]['value']
                
            # Set if they are a broadcaster
            elif e.tags[i]['key'] == 'badges':
                if e.tags[i]['value'] == 'broadcaster/1':
                    self.is_broadcaster = True
                else:
                    self.is_broadcaster = False
                    
            # Set if they are a mod
            elif e.tags[i]['key'] == 'mod':
                if e.tags[i]['value'] == '1':
                    self.is_mod = True
                else:
                    self.is_mod = False

    def check_valid_username(self):
        database = SQLiteConnector()
        username_internal = self.username
        user_id_internal = self.userid
        database.update_username(user_id_internal, username_internal)
