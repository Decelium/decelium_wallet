import sys
import getpass
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
import decelium_wallet.decelium as decelium
import decelium_wallet.crypto as crypto
from sys import getsizeof
from os.path import exists

def run(*args):

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
    print("Enter a password:")
    password1 = getpass.getpass()
    print("Enter password again:")
    password2 = getpass.getpass()
    if password1 != password2:
        print("The passwords don't match")
        sys.exit()    
    path = args[0]
    dw = decelium.SimpleWallet()
    dw.load(path=path,password=password1)
    for user_id in users.keys():
        user_data = users[user_id]
        #print(users[user_id])
        user = dw.create_account(label=user_id,user=user_data)
        dw.set_secret(user_id, 'Example_secret_value', "some_password_123")
    
    dw.save(path=path,password=password1)
    dw = decelium.SimpleWallet()
    dw.load(path=path,password=password1)
    import pprint
    pprint.pprint(dw.get_raw())

if __name__ == "__main__": 
    run(*sys.argv[1:])