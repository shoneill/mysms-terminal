import os
from apiCallsTest import Calls

VERSION = '0.01'

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

def helpScreen():
    print('mysms terminal interface')
    print('version: ' + VERSION + '\n')
    print('commands: ' + availableOptions())

def availableOptions():
    options = ''
    for key in menuOptions:
        options += str(key) + ', '
    return options

def menu():
    while True:
        menuOptions[input('> ')]()

c = Calls()
c.login()

menuOptions = {'clear'       : clearScreen,
               'help'        : helpScreen,
               'listContacts': c.getContacts,
               'listConvos'  : c.getConversations,
               'message'     : c.prepareSMS,
               'c'           : c.getSingleConversation,
               'exit'        : exit
              }

menu()
