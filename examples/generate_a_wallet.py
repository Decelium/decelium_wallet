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
if __name__ == "__main__":
    '''
    This example shows, if you have the api_key and public key of an account, how to generate a wallet. This is 
    a very rare circumstance, and usually only comes up if you have just a private key to work with.
    '''
    users= {
            'test_key_fail':{'api_key': 'x66eebeb3b56bd627c082a36fb0528e45d1fa8d6a1b9e47d478c3af9a11baaf6431bfdb491ceb6d8c5a3674433dcf5a1a1f9af74cf5a9414d026b68fdcedfc5d', 
                            'private_key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 
                            'version': 'python-ecdsa-0.1'},
            }   
    password = "some_very_strong_password"
    path = './example.wallet.dec'
    dw = decelium.SimpleWallet()
    dw.load(path=path,password=password)
    for user_data in users.values():
        user = dw.create_account(user_data)
    dw.save(path=path,password=password)
    dw = decelium.SimpleWallet()
    dw.load(path=path,password=password)
    import pprint
    pprint.pprint(dw.get_raw())
