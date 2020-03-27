# Author: Colin Andress
# Project: Simple Chatbot
# Filename: Data.py
# Description: User object class

import random

from Database.SQLiteConnector import SQLiteConnector

class Data:
    
    def __init__(self, e):
        self.username = None
        self.userid = None
        self.is_broadcaster = False
        self.is_mod = False
        self.user_color = None
        self.has_set_color = False
        self.database = SQLiteConnector()
        
        self.set_information(e)
        if self.has_set_color is False:
            self.set_color()
        
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
                if self.user_color is None:
                    self.has_set_color = False
                else:
                    self.has_set_color = True
                
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
        username_internal = self.username
        user_id_internal = self.userid
        self.database.update_username(user_id_internal, username_internal)
        
    def set_color(self):
        color = self.database.get_user_color(self.userid)
        if color is None:
            name_colors = ["#0000FF", "#ff7f50", "#1e90ff", "#00ff00", "#9acd32", "#00ff00", "#ffd700", "#ff4500", "#ff0000","#ff69b4", "#5f9ea0", "#2e8b57","#d2691e", "#8a2be2", "#b22222"]
            rand_color = random.choice(name_colors)
            self.database.set_user_color(self.userid, rand_color)
            self.user_color = rand_color
        else:
            self.user_color = color