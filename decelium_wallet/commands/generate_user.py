#contract=Command
#version=0.1

import sys, getpass
import unittest    
import uuid    
import json
sys.path.append('../../')
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
class Command:
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

        path = args[0:][0]
        user_id = args[0:][1]
        confirm = None
        if len(args)>2:
            confirm = args[0:][2]
        with open(path,'r') as f:
            print(f.read())
        #with open(path+'.password','r') as f:
        #    print(f.read())
        password = decelium.getpass(path)
        dw = decelium.SimpleWallet()
        dw.load(path=path,password=password)
        user_data = crypto.generate_user()
        user = dw.create_account(label=user_id,user=user_data)
    
        dw.save(path=path,password=password)
        dw = decelium.SimpleWallet()
        dw.load(path=path,password=password)
        raw = dw.get_raw()
        #print(type(raw))
        return json.dumps(raw)
def run(*args):
    c = Command()
    return c.run (args)