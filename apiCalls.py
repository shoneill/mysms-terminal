from apiWrapper import mysmsAPI
import json
import getpass
from operator import itemgetter
from datetime import datetime

class Calls():

    __mysmsAPI = False

    def login(self):
        apiKey = 'API_KEY'

        # initialize API wrapper with key
        self.__mysmsAPI = mysmsAPI(apiKey)

        # user login
#        number = input('Phone number: ')
#        passwd = getpass.getpass()
#        login_data = {'msisdn': str(number), 'password': str(passwd)}
        login_data = {'msisdn': 'PHONE_NUMBER', 'password': 'YOUR PASSWD'}

        login = self.__mysmsAPI.apiCall('/user/login', login_data, False)
        user_info = json.loads(login)

        # Explanation of error codes is here: 
        # http://api.mysms.com/resource_User.html#path__user_login.html
        if(user_info['errorCode'] is not 0):
            raise Exception('Failed to login. Error code is ' + \
                            str(user_info['errorCode'])) 
        else:
            print('Login successful')

        # setting up auth token
        self.__mysmsAPI.setToken(user_info['authToken']) 

    #Lists the user's contacts in alphabetical order
    def getContacts(self):
        data = {} # no required data
        contacts = self.__mysmsAPI.apiCall('/user/contact/contacts/get', data)
        contacts = json.loads(contacts)['contacts']
        names = []
        for contact in contacts:
            names.append(contact['name'])
        names.sort()
        for name in names:
            print(name)

    #Gets the input from the user for who to send a message to and what the
    #message will be. Passes that information to the sendSMS function, which
    #performs the API call
    def prepareSMS(self):
        recInput = input('Enter in recipients separated by spaces: ')
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
            print('Failed to send message. Error: ' +\
            str(json.loads(sendsms)['errorCode']))
        else:
            print('Message sent.')

    #Gets the recent conversations list
    def getConversations(self):
        req_data = {}
        getConvs = self.__mysmsAPI.apiCall('/user/message/conversations/get',\
                                           req_data)
        if json.loads(getConvs)['errorCode'] != 0:
            print('Failed to get conversations. Error: ' +\
            str(json.loads(getConvs)['errorCode']))
        else:
            convs = json.loads(getConvs)['conversations']
            sortedConvs = sorted(convs,key=itemgetter('dateLastMessage'))
            for conv in sortedConvs:
                self.printConvo(self.translateConversation(conv))

    #Takes the POSIX Time in milliseconds and converts it to a human readable
    #date. Note the division by 1000 is necessary to have it in the format of
    #seconds
    def getDate(self, date):
        return datetime.fromtimestamp(int(date/1000))
    
    #Converst the json for a conversation from the API call into something that
    #has the relevant information and is human readable
    def translateConversation(self, conv):
        date    = self.getDate(conv['dateLastMessage'])
        number  = conv['address']
        snippet = conv['snippet']
        return [date, number, snippet]

    #Prints out a one line summary of the conversation data taken from the
    #translated data
    def printConvo(self, translatedConvo):
        print(str(translatedConvo[0]) + ' ' + translatedConvo[1] +
                ' ' + translatedConvo[2])


        
