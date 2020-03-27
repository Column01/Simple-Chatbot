# Author: Colin Andress
# Project: Simple Chatbot
# Filename: helpers.py
# Description: Some helper function(s) used in various classes

def test_list_item(list, index):
    try:
        test = list[index]
        # Supress warning for unused variable
        del test
        return True
    except IndexError:
        return False