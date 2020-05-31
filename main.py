import requests
import hmac
import hashlib
import json
from time import time
import sys

class tuya_api:
    def __init__(self):
        self._isLogged  = False
        self._encode   = 'HMAC-SHA256'

        self.debug     = False
        self.url_api   = "https://openapi.tuyaeu.com"

        with open('code.json') as param_data:
            data = json.load(param_data)
            self.client_id = data['client_id']
            self.secret    = data['app_id']

    def _debug(self, text):
        if self.debug:
            print(text)

    def _getInfo(self):
        print('Timestamp: '+str(self.timestamp))
        print('Signature:'+self.signature)
        print('Token:' + self.token)

    def _getSignature(self, token = False):
        self._debug('Get sign...')
        self.timestamp = int(time()*1000)
        if token:
            message = self.client_id + self.token + str(self.timestamp)   
        else:
            message = self.client_id + str(self.timestamp)

        self.signature = hmac.new(bytes(self.secret , 'latin-1'), msg = bytes(message, 'latin-1'), digestmod = hashlib.sha256).hexdigest().upper()

    def login(self):
        self._debug('Login...')

        self._getSignature()           
        
        header = {
            'client_id'  : self.client_id,
            'sign'       : self.signature,
            't'          : str(self.timestamp),
            'sign_method': 'HMAC-SHA256'
        }

        res = requests.get(self.url_api + '/v1.0/token?grant_type=1', headers=header)

        if res.ok: 
            result = json.loads(res.content)
            if result['success']:
                self.token = result['result']['access_token']
                self._isLogged = True
            else:
                print('Authentification Error: ' + result['msg'])
        else:
            print("HTTP %i - %s, Message %s" % (res.status_code, res.reason, res.text))
    
    def switch(self, id, value):
        if not self._isLogged:
            return

        self._debug("Switch...")
        self._getSignature(True)
        
        header = {
            'client_id'    : self.client_id,
            'access_token' : self.token,
            'sign'         : self.signature,
            't'            : str(self.timestamp),
            'sign_method'  : self._encode,
            'Content-Type' :'application/json'
        }
        
        data = '{\n\t\"commands\":[\n\t\t{\n\t\t\t\"code\": \"switch_1\",\n\t\t\t\"value\":'+value+'\n\t\t}\n\t]\n}' 
        
        res = requests.post(self.url_api + '/v1.0/devices/' + id + '/commands', headers=header, data = data)
        if res.ok:
            result = json.loads(res.content)
            if result['success']:
                self._debug('Device ' + id + 'status set to ' + value)
            else:
                print('Execution Error: ' + result['msg'])   
        else:
            print("HTTP %i - %s, Message %s" % (res.status_code, res.reason, res.text))

    def getStatus(self, id):
        if not self._isLogged:
            return

        self._debug("Get Statuts...")
        self._getSignature(True)        
       
        header = {
            'client_id'    : self.client_id,
            'access_token' : self.token,
            'sign'         : self.signature,
            't'            : str(self.timestamp),
            'sign_method'  : self._encode,
        }

        res = requests.get(self.url_api + '/v1.0/devices/'+ id+ '/status', headers=header)

        if res.ok: 
            result = json.loads(res.content)
            if result['success']:
                return result['result'][0]['value']
            else:
                print('Authentification Error: ' + result['msg'])
        else:
            print("HTTP %i - %s, Message %s" % (res.status_code, res.reason, res.text))


def main():
    tuya = tuya_api()
    tuya.login()
    #tuya.switch(sys.argv[1], sys.argv[2])
main()