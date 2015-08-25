from apiWrapper import mysmsAPI
import json
import getpass
from operator import itemgetter
from datetime import datetime, timedelta, time, date

class Calls():

    __mysmsAPI = False
    
    __contacts = False
    __convos   = False
    __activeConvo = False

    def login(self, number = False, passwd = False):
        apiKey = 'API_KEY'

        # initialize API wrapper with key
        self.__mysmsAPI = mysmsAPI(apiKey)

        # user login
        if not number:
            number = input('Phone number: ')
        if not passwd:
            passwd = getpass.getpass()
        login_data = {'msisdn': str(number), 'password': str(passwd)}

        login = self.__mysmsAPI.apiCall('/user/login', login_data, False)
        user_info = json.loads(login)

        # Explanation of error codes is here: 
        # http://api.mysms.com/resource_User.html#path__user_login.html
        if(user_info['errorCode'] is not 0):
            raise Exception('Login error: ' + \
                            str(user_info['errorCode'])) 

        # setting up auth token
        self.__mysmsAPI.setToken(user_info['authToken']) 

        # loading contacts and conversations
        self.__contacts = self.loadContacts()
        self.__convos = self.loadConversations()

    #Loads the user's contacts into memory as name + number pairs
    def loadContacts(self):
        data = {} # no required data
        contacts = self.__mysmsAPI.apiCall('/user/contact/contacts/get', data)
        if json.loads(contacts)['errorCode'] != 0:
            print('loadContacts error: ' +\
            str(json.loads(contacts)['errorCode']))
        else:
            contacts = json.loads(contacts)['contacts']
            contactList = []
            for contact in contacts:
                tmp = [contact['name'], contact['msisdns']]
                contactList.append(tmp)
            contactList = sorted(contactList, key=itemgetter(0))
            return contactList

    #Grabs the updated conversation list from the server
    def updateConvos(self, options=[]):
        newConvo = self.loadConversations()
        self.__convos = newConvo

    #Prints out the loaded contact info to give names + numbers for all contacts
    def getContacts(self, options=[]):
        if self.__contacts == False:
            self.loadContacts()
        for contact in self.__contacts:
            print(str(contact[0]) + ' ' + str(contact[1]))

            
    #Gets the input from the user for who to send a message to and what the
    #message will be. Passes that information to the sendSMS function, which
    #performs the API call
    def prepareSMS(self, options=[]):
        recInput = input('To (10 digits, space separated): ')
        recipients = recInput.split()
        message = input('Enter your message: ')
        self.sendSMS(recipients, message)

    #Compiles the data into an appropriate format and performs the API call to
    #send the SMS. Prints error codes if there is a problem.
    def sendSMS(self, recipients, message):
        # recipients must have '+1' prefix for US numbers
        req_data = {
            "recipients": recipients,
            "message": message,
            "encoding": 0,
            "smsConnectorId": 0,
            "store": True,
        }

        sendsms = self.__mysmsAPI.apiCall('/remote/sms/send', req_data)
        if json.loads(sendsms)['errorCode'] != 0:
            print('sendSMS error: ' +\
            str(json.loads(sendsms)['errorCode']))
        else:
            print('Message sent.')
    
    #loads all the active conversations from the server into memory
    def loadConversations(self):
        req_data = {}
        getConvs = self.__mysmsAPI.apiCall('/user/message/conversations/get',\
                                           req_data)
        if json.loads(getConvs)['errorCode'] != 0:
            print('loadConversations error: ' +\
            str(json.loads(getConvs)['errorCode']))
        else:
            loadedConvs = []
            convs = json.loads(getConvs)['conversations']
            convs = sorted(convs,key=itemgetter('dateLastMessage'),reverse=True)
            i = 0
            for c in convs:
                loadedConvs.append([str(i), c])
                i += 1
            return loadedConvs

    #Gets the recent conversations list
    def getConversations(self, options=[]):
        if self.__convos == False:
            self.loadConversations()
        limit = 10
        for i in range(limit, -1, -1):
            conv = self.__convos[i]
            print(str(i) + ') ', end='')
            self.printConvoInfo(self.translateConversation(conv[1]))

    #Sets a conversation as the currently focused conversation
    def setActiveConversation(self, conv):
        self.__activeConvo = conv[1]

    def openConversation(self, options=[]):
        if len(options) > 0:
            c = int(options[0])
        else:
            c = int(input('Conv num: '))
        self.setActiveConversation(self.__convos[c])
        self.markConversationRead(self.__activeConvo['address'])
        self.getSingleConversation(self.__activeConvo['address'])

    def replyToActiveConvo(self, options=[]):
        if self.__activeConvo == False:
            print('No active conversation, please open one')
        else:
            address = self.__activeConvo['address']
            if type(address) != list:
                address = [address]
            msg = input('msg: ')
            self.sendSMS(address, msg)

    #Takes POSIX time of the last messages and converts them to a conveniently 
    #readable format. Messages that occur the same day as the current date will
    #only show the timestamp. Messages from yesterday will say "Yesterday" and
    #the time. Messages before that will show the full date.
    def getReadableTime(self, msgTime):
        today = datetime.combine(date.today(), time.min)
        yesterday = datetime.combine(today + timedelta(-1), time.min)
        msgDate = datetime.fromtimestamp(int(msgTime/1000))
        if msgDate > today:
            return msgDate.strftime('%H:%M')
        elif msgDate > yesterday:
            return "Yesterday " + msgDate.strftime('%H:%M')
        else:
            return msgDate.strftime('%b %d, %H:%M')
        
    #Converst the json for a conversation from the API call into something that
    #has the relevant information and is human readable
    def translateConversation(self, conv):
        date    = self.getReadableTime(conv['dateLastMessage'])
        number  = self.convertNumberToName(conv['address'])
        snippet = conv['snippet']
        return [date, number, snippet]

    #Prints out a one line summary of the conversation data taken from the
    #translated data
    def printConvoInfo(self, translatedConvo):
        print(str(translatedConvo[0]) + ' ' + translatedConvo[1] +
                ' ' + translatedConvo[2])

    #Taking in conversation info prints out the conversation in a readable
    #format    
    def getSingleConversation(self, number):
        address = number
        offset  = 0
        limit   = 10
        req_data = {
            'address': address,
            'offset' :  offset,
            'limit'  :   limit
        }
        getConv = self.__mysmsAPI.apiCall('/user/message/get/by/conversation',\
                                          req_data)
        if json.loads(getConv)['errorCode'] != 0:
            print('getSingleConversations. Error: ' +\
            str(json.loads(getConv)['errorCode']))
        else:
            getConv = json.loads(getConv)['messages']
            self.translateSingleConv(getConv)
    
    def translateSingleConv(self, conv):
        conv.reverse()
        for line in conv:
            read = '' if line['read'] else '*'
            name = self.convertNumberToName(line['address']) \
                    if line['incoming'] else 'You'
            msg = line['message']

            print(read + name + ': ' + msg)

    #Marks a conversation as read
    def markConversationRead(self, number):
        address = number
        req_data = {
            'address': address
        }
        markRead = self.__mysmsAPI.apiCall('/user/message/conversations/read',\
                                           req_data)

        if json.loads(markRead)['errorCode'] != 0:
            print('markConversationRead error: ' +\
            json.loads(genConv)['errorCode'])

    #Returns the number of unread messages
    def numUnreadMessages(self, options=[]):
        numUnread = 0
        for conv in self.__convos:
            numUnread += conv[1]['messagesUnread']
        return numUnread

    def convertNumberToName(self, number):
        for contact in self.__contacts:
            for num in contact[1]:
                if num == number:
                    return contact[0]
        return number
