#contract=Command
#version=0.1

import sys, getpass,json, os
import uuid    
sys.path.append('../../')
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
        path = args[0:][0]
        #print("display_wallet cwd", os.getcwd())
        password = decelium.getpass(path)
        dw = decelium.SimpleWallet()
        dw.load(path=path,password=password)
        return json.dumps(dw.get_raw())    

def run(*args):
    c = Command()
    return c.run (args)