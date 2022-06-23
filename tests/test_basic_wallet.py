import sys
import pandas as pd
import unittest    
import uuid    
import json
sys.path.append('../../')
import pandas as pd
import requests
import datetime,time
import unittest
import uuid
import decelium.decelium as decelium
import decelium.crypto as crypto
from sys import getsizeof
from os.path import exists

'''
class OpenDeceliumWallet():
    '''
    A simple open source wallet for holding decelium network artifacts. This wallet is a code level
    wallet only, and does not have a GUI for user interaction. Volunteers are presently working on
    hardware, javascript, and GUI wallet implementations! 

    Why? We had a lot of problems in web 3.0 with three issues:
    - sign transactions
    - store accounts and addresses
    - store generic secrets, keeping them encrypted too
    '''

    def load(self,path=None):
        self.wallet = {}
        if path != None:
            if not exists(path):
                return
            with open(path,'r') as f:
                astr = f.read()
                self.wallet= crypto.crypto.do_decode_string(astr )

    def save(self,path):
        with open(path,'w') as f:
            dumpstr = crypto.crypto.do_encode_string(self.wallet)
            f.write(dumpstr)
        with open(path,'r') as f:
            savedstr = f.read()
            assert dumpstr == savedstr

    def request_sign(self,message):
        '''
        Request a signature on a message from the user.
        '''
        print("Authorizing message")
        return True

    def create_account(self):
        user = crypto.crypto.generate_user(version='python-ecdsa-0.1')
        assert 'api_key' in user
        assert 'private_key' in user
        assert 'version' in user
        account_data = {'user':user,
                        'title':user['api_key'],
                        'image':None,
                        'description':None,
                        'secrets':{},
                        'watch_addresses':[]}
        self.wallet[user['api_key']] = account_data
        return user['api_key']

    def list_accounts(self):
        return list(self.wallet.keys())

    def get_account(self,api_key):
        if not api_key in self.wallet:
            return {'error':'User is not in wallet manager'}
        return self.wallet[user['api_key']] 

    def get_user(self,api_key):
        if not api_key in self.wallet:
            return {'error':'User is not in wallet manager'}
        return self.wallet[api_key]['user'] 

    def set_secret(self,api_key, sid,sjson):
        if not api_key in self.wallet:
            return {'error':'User is not in wallet manager'}
        try:
            a_string = crypto.crypto.do_encode_string(sjson)
        except:
            return {'error':'could not encode secret as json'}

        if getsizeof(a_string) > 1024*2:
            return {'error':'can not store a secret larger than 2kb'}

        self.wallet[api_key]['secrets'][sid] = sjson 
        return True
    
    def get_secret(self,api_key, sid):
        if not api_key in self.wallet:
            return {'error':'User is not registered'}
        if not sid in self.wallet[api_key]['secrets']:
            return {'error':'secret not saved'}
        return self.wallet[api_key]['secrets'][sid] 

    def get_raw(self):
        return this.wallet

    def recover_user(self,private_key):
        return crypto.crypto.generate_user_from_string(private_key,version='python-ecdsa-0.1')
'''

class TestBasicWallet(unittest.TestCase):     
    def __init__(self, *args, **kwargs):
        super(TestBasicWallet, self).__init__(*args, **kwargs)
        #self.create_test_wallet()

    def create_test_wallet(self):
        url_version = 'dev.paxfinancial.ai'
        path = './test.wallet.dec'
        dw = OpenDeceliumWallet()
        dw.load(path)
        dw.create_account()
        k = dw.list_accounts()[0]
        user = dw.get_user(k)
        print(user)
        pq_raw = decelium.Decelium(url_version=url_version,api_key=user['api_key'])
        self.pq = decelium.SimpleCryptoRequester(pq_raw,{user['api_key']:user})
        return self.pq,user['api_key']      

    def test_wallet_storage(self,pq = None,api_key=None,remote=True):
        # - Save load local user (memory) (1-2 hrs)
        # - Add user
        # - test secret
        # - remove secret
        # - delete file
        print(pq)
        print(api_key)
        print(remote)
        print("hey brian")

    def test_create_local_user(self,pq = None,api_key=None,remote=True):
        # test remote user
        print("hey alex")

    def test_create_website(self,pq = None,api_key=None,remote=True):
        # full website test
        print("hey steph")
    # TODO - Github Docs
    # TODO - dev - stage - live + announcement
    #

if __name__ == "__main__":
    tbw = TestBasicWallet()
    [pq,api_key] = tbw.create_test_wallet()
    remote = True
    tbw.test_wallet_storage(pq,api_key,remote)
