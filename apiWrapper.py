import json
import pycurl
import io

class mysmsAPI():

    #Location of where the API calls will be made
    __apiURL = 'https://api.mysms.com/'

    #API Key and Auth Token need to be provided
    __key       = False
    __AuthToken = False

    #By default they key and token are set to false until given by the user
    def __init__(self, APIKey = False, token = False):
        self.__key = APIKey
        self.__AuthToken = token
    
    def setKey(self, key):
        self.__key = key

    def setToken(self, token):
        self.__AuthToken = token


    def apiCall(self, resource, data, authToken = True):
        contentFormat = 'json' #Preferred to use JSON format for calls

        if not isinstance(data, (list, tuple, dict)): #Checks for valid data
            raise Exception('Data must be provided as an array')
        else:
            data['apiKey']    = self.__key
            
            if authToken:
                data['authToken'] = self.__AuthToken

            call = self.curl(contentFormat + resource, data).decode('utf-8')
            
            return call

    def curl(self, resource, data):
        #encoding the data into json
        json_data = json.dumps(data)

        #Performing the curl to the api
        crl = pycurl.Curl()
        crl.setopt(pycurl.URL, self.__apiURL + resource)
        crl.setopt(pycurl.POSTFIELDS, json_data)
        crl.setopt(pycurl.HTTPHEADER, [\
            'Content-Type: application/json;charset=utf-8',\
            'Content-Length: ' + str(len(json_data))])
        out = io.BytesIO()
        crl.setopt(pycurl.WRITEFUNCTION, out.write)

        crl.perform()
        return out.getvalue()
