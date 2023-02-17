import sys
sys.path.append("../../")
sys.path.append("../../../")
from decelium_wallet.crypto import crypto
from decelium_wallet import decelium
import getpass

def load_pq(path,password,url_version,target_user):
    dw = decelium.SimpleWallet()
    dw.load(path,password)
    accts = dw.list_accounts()

    #print(accts)
    #print(dw.get_user('admin'))

    assert target_user in accts
    user = dw.get_user(target_user)
    pq_raw = decelium.Decelium(url_version=url_version,api_key=user['api_key'])
    pq = decelium.SimpleCryptoRequester(pq_raw,{user['api_key']:user})
    return pq, user['api_key'], dw

def run(*args):

    wallet_path = args[0]
    password = crypto.getpass()
    wallet_user = args[1]
    dec_username = args[2]
    url_version = args[3]
    
    [pq,api_key,wallet] = load_pq(wallet_path,password,url_version,wallet_user)
    
    print(api_key)
    
    #dw = decelium.SimpleWallet()
    #dw.load(path=wallet_path,password=password)
    wallet_contents = wallet.get_raw()
    
    access_keys = wallet_contents[wallet_user]['user'].copy()
    access_keys['private_key'] = "deadbeef"
    
    print("Enter the password for the user on Decelium:")
    password = getpass.getpass()
    print("Reenter the password for the user on Decelium:")
    password2 = getpass.getpass()
    if password != password2:
        print("The passwords don't match.")
        sys.exit()
    
    feature = {'username': dec_username,
               'api_key': api_key,
               'access_key':access_keys,
               'password': password,
               'password2': password2,}
    result = pq.delete_entity({'api_key':api_key,'path':'system_users','name':dec_username,},remote=True)   
    obj_id = pq.user_register(feature,remote=True)
    print(obj_id) 

if __name__ == "__main__":

    run(*sys.argv[1:])