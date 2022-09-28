import sys
sys.path.append('../../')
sys.path.append('../../../')
from decelium.crypto import crypto
from decelium import decelium
import uuid
import base64
import pprint
import shutil
import getpass
#from dotenv import load_dotenv

def load_pq(path,password,url_version):
    dw = decelium.SimpleWallet()
    dw.load(path,password)
    accts = dw.list_accounts()
    
    print(accts)
    #print(dw.get_user('admin'))
    
    assert 'admin' in accts
    user = dw.get_user('admin')
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
if __name__ == "__main__":
    import os 
    dir_path = os.path.dirname(os.path.realpath(__file__))    
    os.chdir(dir_path)
    cfg = get_env_data_as_dict(sys.argv[1:][0])
    print(cfg)
    
    wallet_path = sys.argv[1:][1]
    #url_version = sys.argv[1:][2]
    url_version =cfg ['PY_URL_VERSION'] 
    
    password = getpass.getpass()

    with open("ProcessPayment.py",'r') as contract_py:
        func_data= contract_py.read()
        func_data = func_data.replace("<<STRIPE_API_KEY>>",cfg["PY_STRIPE_API_KEY"])
    root_path= cfg["PY_ROOT_DIR"] #'/decelium_payment_example/' 
 
    [pq,api_key,wallet] = load_pq(wallet_path,password,url_version)
    print({'api_key':api_key, 'path':root_path, })
    for item in pq.list({'api_key':api_key, 'path':root_path, },remote=True):
        print(item['error'])
        print("deployed... ", item['self_id'], ' as ', item['dir_name'])
        