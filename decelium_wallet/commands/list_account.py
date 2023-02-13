import sys
sys.path.append('../../')
sys.path.append('../../../')
from decelium_wallet.crypto import crypto
from decelium_wallet import decelium
import uuid
import base64
import pprint
import shutil
import getpass
#from dotenv import load_dotenv

def load_pq(path,password,url_version,target_user):
    dw = decelium.SimpleWallet()
    dw.load(path,password)
    accts = dw.list_accounts()
    
    print(accts)
    #print(dw.get_user('admin'))
    
    assert target_user in accts
    user = dw.get_user(target_user)
    pq_raw = decelium.Decelium(url_version=url_version,api_key=user['api_key'])
    pq = decelium.SimpleCryptoRequester(pq_raw,{user['api_key']:user})
    return pq, user['api_key'], dw

def get_env_data_as_dict(path: str) -> dict:
    with open(path, 'r') as f:
        try:
            return dict(tuple(line.replace('\n', '').split('=')) for line
                        in f.readlines() if not line.startswith('#'))
        except Exception as e:
            print(path)
            print(f.read())
            raise e
            
def run(*args):
    wallet_path = args[0]
    target_user = args[1]
    url_version = args[2]
    root_directory = args[3]
    
    password = crypto.getpass()
 
    [pq,api_key,wallet] = load_pq(wallet_path,password,url_version,target_user)
    q={'api_key':api_key, 'path':root_directory, }
    print(q)
    for item in pq.list(q,remote=True):
        #print(item['error'])
        print("deployed... ", item['self_id'], ' as ', item['dir_name'])    
    
if __name__ == "__main__":
    run(*sys.argv[1:])
    

        