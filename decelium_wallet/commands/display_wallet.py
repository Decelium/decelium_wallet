import sys, getpass
import uuid    
sys.path.append('../../')
import decelium.decelium as decelium
import decelium.crypto as crypto
from sys import getsizeof
from os.path import exists
if __name__ == "__main__":
    '''
    This example shows, if you have the api_key and public key of an account, how to generate a wallet. This is 
    a very rare circumstance, and usually only comes up if you have just a private key to work with.
    '''
    #path = '../../.wallet.dec'
    path = sys.argv[1:][0]
    password = getpass.getpass()
    dw = decelium.SimpleWallet()
    dw.load(path=path,password=password)
    import pprint
    pprint.pprint(dw.get_raw())
