# Author: Colin Andress
# Project: Simple Chatbot
# Filename: Data.py
# Description: User object class

import random

from Database.SQLiteConnector import SQLiteConnector


class Data:
    
    def __init__(self, event):
        self.username = None
        self.userid = None
        self.is_broadcaster = False
        self.is_mod = False
        self.user_color = None
        self.has_set_color = False
        self.event = event
        self.database = SQLiteConnector()
        
        self.set_information()
        if self.has_set_color is False:
            self.set_color()
        
    def set_information(self):
        for i in range(len(self.event.tags)):
            # Set their username
            if self.event.tags[i]['key'] == 'display-name':
                self.username = self.event.tags[i]['value']
                
            # Set their userid
            elif self.event.tags[i]['key'] == 'user-id':
                self.userid = self.event.tags[i]['value']
                
            # Set their user color
            elif self.event.tags[i]['key'] == "color":
                self.user_color = self.event.tags[i]['value']
                if self.user_color is None:
                    self.has_set_color = False
                else:
                    self.has_set_color = True
                
            # Set if they are a broadcaster
            elif self.event.tags[i]['key'] == 'badges':
                if self.event.tags[i]['value'] == 'broadcaster/1':
                    self.is_broadcaster = True
                else:
                    self.is_broadcaster = False
                    
            # Set if they are a mod
            elif self.event.tags[i]['key'] == 'mod':
                if self.event.tags[i]['value'] == '1':
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
            name_colors = ["#0000FF", "#ff7f50", "#1e90ff", "#00ff00", "#9acd32", "#00ff00", "#ffd700", "#ff4500", "#ff0000", "#ff69b4", "#5f9ea0", "#2e8b57", "#d2691e", "#8a2be2", "#b22222"]
            rand_color = random.choice(name_colors)
            self.database.set_user_color(self.userid, rand_color)
            self.user_color = rand_color
        else:
            self.user_color = color
