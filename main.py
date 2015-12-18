#!/usr/bin/python
import sys
import json
import logging
import argparse

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from oauth2 import auth
from oauth2.request import WebRequest
from oauth2.helpers import load, save


URI_EXPORT = 'https://script.google.com/feeds/download/export?id=%s&format=json'
URI_DRIVE = 'https://www.googleapis.com/upload/drive/v2/files'

BUILD_DIR = 'build'
OAUTH2_CLIENT = "client_secret.json"
OAUTH2_TOKENS = "tokens.json"


class gas(object):
    """docstring for gas"""
    def __init__(self, userId):
        super(gas, self).__init__()
        self.userId = userId
        
        client = load(OAUTH2_CLIENT).get('installed')
        tokens = load(OAUTH2_TOKENS)
        client_id = client.get('client_id')
        client_secret = client.get('client_secret')
        scope = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.scripts']
        
        self.auth = auth.Authenticator(client_id, client_secret, scope, tokens)
    
    def create(self, data = None):
        """docstring for create"""
        url = URI_DRIVE
        
        url_params = {
            "convert": "true"
        }
        
        options = {
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/vnd.google-apps.script+json'
            },
            'params': url_params,
            'data': data
        }
        
        r = self.auth.signedRequest(url, self.userId, **options)
        if r.ok:
            return r.json()
    
    def export(self, fileId):
        """docstring for export"""
        url = URI_EXPORT % fileId
        r = self.auth.signedRequest(url, self.userId)
        
        if r.ok:
            return r.json()
    
    def update(self, fileId, data):
        """docstring for update"""
        url = URI_DRIVE + '/' + fileId
        
        options = {
            'method': 'PUT',
            'headers': {
                'Content-Type': 'application/vnd.google-apps.script+json'
            },
            'data': data
        }
        
        r = self.auth.signedRequest(url, self.userId, **options)
        if r.ok:
            return r.json()
    
    def __del__(self):
        """docstring for __del__"""
        save(self.auth.tokens, OAUTH2_TOKENS)

def main():
    """docstring for main"""
    
    # initialize Arg-parser
    parser = argparse.ArgumentParser()
    
    # setup Arg-parser
    parser.add_argument('-u', '--userId', type=str, help='Email address of your account')
    parser.add_argument('-s', '--sourceFile', type=str, help='ID of your source file')
    parser.add_argument('-t', '--targetFile', type=str, help='ID of your target file')
    
    # initialize args
    args = sys.argv[1:]
    
    # parse arguments
    args, unknown = parser.parse_known_args(args)
    # print args, unknown
    # sys.exit(0)
    
    userId = args.userId or raw_input('Please enter the email address of your account: ')
    
    if userId:
        myGAS = gas(userId)
        
        sourceFile = args.sourceFile or raw_input('Please paste the id of your source file: ')
        newData = myGAS.export(sourceFile)
        
        targetFile = args.targetFile or raw_input('Please paste the id of your target file: ')
        oldData = myGAS.export(targetFile)
        
        if newData and oldData:
            # TODO: iterate through all of them
            newData['files'][0]['id'] = oldData['files'][0]['id']
            result = myGAS.update(targetFile, json.dumps(newData))
        elif newData:
            result = myGAS.create(json.dumps(newData))
        else:
            result = "Nothing to do."
        
        print result

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print "Quitting."