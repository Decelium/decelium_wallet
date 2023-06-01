#contract=Command
#version=0.1


import sys
sys.path.append('../../')
sys.path.append('../../../')
try:
    from decelium_wallet.crypto import crypto
except:
    from crypto import crypto
try:    
    from decelium_wallet import decelium
except:
    import decelium
import uuid
import base64
import pprint
import shutil
import getpass
#from dotenv import load_dotenv
class Command:
    def load_pq(self,path,password,url_version,target_user):
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

    def get_env_data_as_dict(self,path: str) -> dict:
        with open(path, 'r') as f:
            try:
                return dict(tuple(line.replace('\n', '').split('=')) for line
                            in f.readlines() if not line.startswith('#'))
            except Exception as e:
                print(path)
                print(f.read())
                raise e

    def run(self,*args):
        wallet_path = args[0]
        target_user = args[1]
        url_version = args[2]
        root_directory = args[3]

        password = crypto.getpass(wallet_path)

        [pq,api_key,wallet] = load_pq(wallet_path,password,url_version,target_user)
        print({'api_key':api_key, 'path':root_directory, })
        result = pq.download_entity({'api_key':api_key, 'path':root_directory, 'attrib':True},remote=True)
        print(result)

def run(*args):
    c = Command()
    return c.run (args)