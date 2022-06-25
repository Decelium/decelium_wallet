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
import sys


class TestBasicWallet(unittest.TestCase):     
    def __init__(self, *args, **kwargs):
        super(TestBasicWallet, self).__init__(*args, **kwargs)
        #self.create_test_wallet()

    def test_user_setup(self,pq = None,api_key=None,remote=True):
        # Set up a wallet from scratch        
        path = './test-'+str(uuid.uuid4())+'.wallet.dec'
        dw = decelium.SimpleWallet()
        dw.load(path=path)
        user = dw.create_account()
        dw.rename(user['api_key'],'admin')
        dw.save(path=path,password="Example_password")
        dw = decelium.SimpleWallet()
        dw.load(path=path,password="Example_password")
        print(dw.get_raw())
        
    def test_create_website(self,pq = None,api_key=None,remote=True):
        path = '../.wallet.dec'
        password = sys.argv[1:][0]
        dw = decelium.SimpleWallet()
        dw.load(path,password)
        accts = dw.list_accounts()
        assert 'admin' in accts
        #print(dw.get_user('admin'))

        # Network Connection
        user = dw.get_user('admin')
        url_version = 'dev.paxfinancial.ai'
        pq_raw = decelium.Decelium(url_version=url_version,api_key=user['api_key'])
        pq = decelium.SimpleCryptoRequester(pq_raw,{user['api_key']:user})
        
        # Create Site
        data  = pq.delete_entity({'api_key':user['api_key'],'path':'/html_files/'+'index.html'},remote=remote)
        website = '''<!DOCTYPE html>
<html>
<body>
<h1>Generic Headin 2</h1>
<p>Generic paragraph.</p>
</body>
</html>'''
        
        res_obj =pq.create_entity({'api_key':user['api_key'],  'path':'/html_files/', 
                                    'name':'index.html','file_type':'file', 
                                    'payload':website,},remote=remote)
        print(res_obj)        
        res_data =pq.download_entity({'api_key':user['api_key'], 'path':'/html_files/index.html'},remote=remote)
        print(res_data)        
        assert website==res_data
        '''https://test.paxfinancial.ai/obj/obj-153f2733-4ac6-4b35-a375-cf228f5892c9'''
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
    #tbw.test_user_setup(pq=None,api_key=None,remote=True)
    tbw.test_create_website(pq=None,api_key=None,remote=True)
    
