from apiCallsTest import Calls

def menu():
    while True:
        menuOptions[input('option: ')]()

c = Calls()
c.login()

menuOptions = {'contacts': c.getContacts,
               'message' : c.prepareSMS,
               'convos'  : c.getConversations,
               'exit': exit
              }

menu()
