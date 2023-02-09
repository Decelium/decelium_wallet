import os
import sys
 
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')

original_stdout = sys.stdout
sys.stdout = open("/dev/null","w")
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

class Deploy():

    def explain(self):
        return "wallet_path target_user command secret_id secret_value secret_value"

    def run(self,*args):
        wallet_path = args[0]
        target_user = args[1]
        command = args[2]    
        secret_id = None    
        secret_value = None
        if len(args) > 3:
            secret_id = args[3]    
        if len(args) > 4:
            secret_value = args[4]

        password = crypto.getpass()
        #print(password)
        #print(wallet_path)
        wallet = decelium.SimpleWallet()
        wallet.load(wallet_path,password)
        accts = wallet.list_accounts()
        #print(wallet.wallet)
        assert target_user in accts   
        if command == "list":
            wallet.list_secrets(target_user)
            print(wallet.list_secrets(target_user))

        if command == "add":
            shutil.copy(wallet_path, wallet_path+'.backup')        
            secret_passcode = wallet.set_secret(target_user, secret_id,secret_value)
            wallet.save(wallet_path,password)
            print(1)
        
        if command == "view":
            secret_passcode = wallet.get_secret(target_user, secret_id)
            print(secret_passcode)
    
    def get_password(self):
        for prefix in ['./','../','../../']:
            filename = prefix+".password"
            #print(filename)
            if os.path.exists(filename):
                f = open(filename, 'r')
                password = f.read()
                f.close()
                break
        else:
            password = crypto.getpass()
       #print("password="+str(password))
        return password        
if __name__ == "__main__":
    direc = '/'.join(__file__.split('/')[:-3]) +'/'
    c = Deploy()
    c.run(*sys.argv[1:])
# python3 secret.py ../../../.wallet.dec admin view decelium_com_dns_code 
# python3 secret.py ../../../.wallet.dec admin list 
# python3 secret.py ../../../.wallet.dec admin add testdecelium_com_dns_code "NEW VAL"
# python3 secret.py ../../../.wallet.dec admin add decelium_com_dns_code "NER VAL"
