#contract=Generate
#version=0.1
#description= A smart contract that can generate wallets on this local machine. Intended to be used locally.
import sys
import getpass
import unittest    
import uuid    
import json
sys.path.append('../../')
sys.path.append('../')
sys.path.append('../../../')
import datetime,time
import unittest
import uuid
try:
    import decelium_wallet.decelium as decelium
except:
    import decelium
try:    
    from decelium_wallet.crypto import crypto
except:
    from crypto import crypto
from sys import getsizeof
from os.path import exists

class Generate:
    def run(self,args):

        '''
        This example shows, if you have the api_key and public key of an account, how to generate a wallet. This is 
        a very rare circumstance, and usually only comes up if you have just a private key to work with.
        '''
        '''
        users= {
                'test_key_fail':{'api_key': 'x66eebeb3b56bd627c082a36fb0528e45d1fa8d6a1b9e47d478c3af9a11baaf6431bfdb491ceb6d8c5a3674433dcf5a1a1f9af74cf5a9414d026b68fdcedfc5d', 
                                'private_key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 
                                'version': 'python-ecdsa-0.1'},
                }
        '''
        users = {

        }

        path = args[0]
        password = decelium.getpass(path)
        
        dw = decelium.SimpleWallet()
        dw.load(path=path,password=password)
        for user_id in users.keys():
            user_data = users[user_id]
            #print(users[user_id])
            user = dw.create_account(label=user_id,user=user_data)
            #dw.set_secret(user_id, 'Example_secret_value', "some_password_123")
                
        dw.save(path=path,password=password)
        
        dw = decelium.SimpleWallet()
        dw.load(path=path,password=password)
        import pprint
        raw = dw.get_raw()
        #print("LOADING")
        #print(dw.get_raw())        
        return json.dumps(raw)
    
def run(*args):
    c = Generate()
    #print("generate_a_wallet args",args)
    return c.run (args)