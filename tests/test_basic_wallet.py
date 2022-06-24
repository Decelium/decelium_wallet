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
        Request a signature on a message from the user.
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
    '''
    def create_test_wallet(self):
        url_version = 'dev.paxfinancial.ai'
        path = './test.wallet.dec'
        dw = OpenDeceliumWallet()
        dw.load(path)
        user = dw.create_account()
        pq_raw = decelium.Decelium(url_version=url_version,api_key=user['api_key'])
        self.pq = decelium.SimpleCryptoRequester(pq_raw,{user['api_key']:user})
        
        return self.pq,user['api_key']      
    '''

    def test_user_setup(self,pq = None,api_key=None,remote=True):
        # Set up a wallet from scratch        
        path = './test-'+str(uuid.uuid4())+'.wallet.dec'
        dw = decelium.SimpleWallet()
        dw.load(path)
        user = dw.create_account()
        dw.save(path,"Test_password")
        dw = decelium.SimpleWallet()
        dw.load(path,"Test_password")
        print(dw.get_raw())
        
        # print(pq)
        # print(api_key)
        # print(remote)
        # print("hey brian")

    def test_create_website(self,pq = None,api_key=None,remote=True):
        # Set up a wallet from scratch        
        path = './test-'+str(uuid.uuid4())+'.wallet.dec'
        app_dir = './test-app-'+str(uuid.uuid4())+'/'

        # Wallet
        dw = decelium.SimpleWallet()
        dw.load(path)
        user = dw.create_account()
        dw.save(path,"Test_password")
        dw = decelium.SimpleWallet()
        dw.load(path,"Test_password")
        print(dw.get_raw())

        # Network Connection
        url_version = 'dev.paxfinancial.ai'
        pq_raw = decelium.Decelium(url_version=url_version,api_key=user['api_key'])
        pq = decelium.SimpleCryptoRequester(pq_raw,{user['api_key']:user})
        
        # Create Site
        data  = pq.delete_entity({'api_key':user['api_key'],'path':'/apps/'+app_dir+'/html_files/'+'index.html'},remote=remote)
        website = '''<!DOCTYPE html>
<html>
<body>
<h1>Generic Heading</h1>
<p>Generic paragraph.</p>
</body>
</html>'''
        
        res_obj =pq.create_entity({'api_key':user['api_key'],  'path':'/apps/'+app_dir+'/html_files/', 
                                    'name':'index.html','file_type':'file', 
                                    'payload':website,},remote=remote)
        print(res_obj)        
        res_data =pq.download_entity({'api_key':user['api_key'], 'path':'/apps/'+app_dir+'/html_files/index.html'},remote=remote)
        print(res_data)        
        assert website==res_data
        '''https://dev.paxfinancial.ai/obj/obj-153f2733-4ac6-4b35-a375-cf228f5892c9'''
        '''
        res_url =pq.create_entity({'api_key':api_key,
                                    'path':'/apps/'+app_dir+'/domains/',
                                    'name':domain,
                                    'file_type':'host',
                                    'attrib':{'host':domain,
                                                'secret_password':secret_password,
                                                'target_id':res_obj}
                                },remote=remote)
        
        print("4",res_url)
        assert 'obj-' in res_url
        return True
        '''
        #

if __name__ == "__main__":
    tbw = TestBasicWallet()
    # Set up query engine
    remote = True
    tbw.test_user_setup(pq=None,api_key=None,remote=True)
    tbw.test_create_website(pq=None,api_key=None,remote=True)
    
