import sys, getpass
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
if __name__ == "__main__":
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
    #path = '../../.wallet.dec'
    #path = '../../.wallet.dec'
    path = sys.argv[1:][0]
    user_id = sys.argv[1:][1]
    password = crypto.getpass()
    dw = decelium.SimpleWallet()
    dw.load(path=path,password=password)
    user_data = crypto.crypto.generate_user()
    user = dw.create_account(label=user_id,user=user_data)
    print("Are you sure you want to write this user? you should backup your wallet first!! (yes/no)")
    print(user_id+":")
    print(user)
    yes = getpass.getpass()
    if yes != "yes" and yes != "y":
        print("aborted. exit..")
        sys.exit(0)
    else:
        print("saving..")
        #dw.set_secret(user_id, 'Example_secret_value', "some_password_123")
        dw.save(path=path,password=password)
        dw = decelium.SimpleWallet()
        dw.load(path=path,password=password)
        import pprint
        pprint.pprint(dw.get_raw())
