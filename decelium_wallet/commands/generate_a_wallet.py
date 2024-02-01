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
import argparse
import traceback

class Generate:
    def run(self,args):
        users = {

        }
        path = args[0]
        try:
            password = decelium.getpass(path)
        except:
            password = None
        if password == None or password == "":
            print("Could not find password in "+args['wallet_path']+".password") 
            return {"error":"Could not find password in "+args['wallet_path']+".password"}

        dw = decelium.SimpleWallet()
        dw.load(path=path,password=password)
        for user_id in users.keys():
            user_data = users[user_id]
            user = dw.create_account(label=user_id,user=user_data)
                
        dw.save(path=path,password=password)
        
        dw = decelium.SimpleWallet()
        dw.load(path=path,password=password)
        import pprint
        raw = dw.get_raw()
        return json.dumps(raw)
    
def run(*args):
    c = Generate()
    #print("generate_a_wallet args",args)
    return c.run (args)