import sys, getpass
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

def run(*args):
    path = args[0:][0]
    password = crypto.getpass()
    dw = decelium.SimpleWallet()
    dw.load(path=path,password=password)
    import pprint
    pprint.pprint(dw.get_raw())    

if __name__ == "__main__":
     run(*sys.argv[1:])

