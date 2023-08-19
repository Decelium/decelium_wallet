#contract=Command
#version=0.1

import os
import sys
 
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')

original_stdout = sys.stdout
sys.stdout = open(os.devnull,"w")
try:
    # Default to the locally installed wallet
    import decelium_wallet.decelium as decelium
    from decelium_wallet.crypto import crypto
    from decelium_wallet.chunk import Chunk

except:        
    # Otherwise use the pip package
    from decelium.crypto import crypto
    from decelium.chunk import Chunk
    import decelium.decelium as decelium


sys.stdout = original_stdout

import uuid
import base64
import pprint
import shutil     
import json
import time
class Command:
    def explain(self):
        return "wallet_path target_user command secret_id secret_value secret_value"

    def run(self,args):
        #print(args)
        
        wallet_path = args[0]
        target_user = args[1]
        command = args[2]    
        secret_id = None    
        secret_value = None
        if len(args) > 3:
            secret_id = args[3]    
        if len(args) > 4:
            secret_value = args[4]

        password = decelium.getpass(wallet_path)
        #print(password)
        #print(wallet_path)
        wallet = decelium.SimpleWallet()
        wallet.load(wallet_path,password)
        accts = wallet.list_accounts()
        #print(accts)
        #print(wallet.wallet)
        assert target_user in accts   
        if command == "list":
            wallet.list_secrets(target_user)
            return json.dumps(wallet.list_secrets(target_user))

        if command == "add":
            shutil.copy(wallet_path, wallet_path+'.backup')        
            secret_passcode = wallet.set_secret(target_user, secret_id,secret_value)
            return json.dumps(wallet.save(wallet_path,password))

        if command == "view":
            secret_passcode = wallet.get_secret(target_user, secret_id)
            return json.dumps(secret_passcode)

    

    
def run(*args):
    c = Command()
    return c.run (args)