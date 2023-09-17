#contract=Deploy
#version=0.1


import os
import sys
 
sys.path.append('../../')
sys.path.append('../../../')

original_stdout = sys.stdout
sys.stdout = open("/dev/null","w")
from decelium_wallet.crypto import crypto
from decelium_wallet import decelium
sys.stdout = original_stdout

import uuid
import base64
import pprint
import shutil     
import json
import time

class Deploy():
    def _load_pq(self,path,password,url_version,target_user):
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

    def deploy_dns(self,pq,api_key,name,target_id,secret_passcode):
        remote=True
        l = pq.list({'api_key':api_key, 'attrib':{'host':name}, },remote=True)
        print(l)
        for item in l:
            print("REMOVING "+str(item))   
            fil  = pq.delete_entity({'api_key':api_key, 
                                    'self_id':item['self_id'], 
                                    },remote=remote) # show_url=True to debug
            
        fil  = pq.delete_entity({'api_key':api_key, 
                                'path':'/_dns/'+name,
                                'name':name, 
                                },remote=remote) # show_url=True to debug

        try:
            print("delete"+fil)             
        except:
            pass               
        assert fil == True or 'error' in fil
        if not 'obj-' in target_id:
            site_obj =pq.download_entity({'api_key':api_key,
                                    'path':target_id,
                                    'attrib':True,
                                    },remote=remote)
            if 'error' in site_obj:
                return  site_obj
            if not 'self_id' in site_obj:
                return {"error":"could not download_entity "+str(site_obj)}
            target_id = site_obj['self_id']
        
        res_url =pq.create_entity({'api_key':api_key,
                                'path':'/_dns/'+name,
                                'name':name,
                                'file_type':'host',
                                'attrib':{'host':name,
                                            'secret_password':secret_passcode,
                                            'target_id':target_id}
                                },remote=remote)
        print(res_url)
        #assert 'obj-' in res_url
        return res_url


    def get_password():
        for prefix in ['./','../','../../']:
            filename = prefix+".password"
            print(filename)
            if os.path.exists(filename):
                f = open(filename, 'r')
                password = f.read()
                f.close()
                break
        else:
            password = decelium.getpass()
        print("password="+str(password))
        return password

    def explain(self):
        return "wallet_path target_user url_version target_id domain"

    def run(self,args):
        #raise Exception("not supported, please use deploy.py")
        #dir_path = os.path.dirname(os.path.realpath(__file__))    
        #os.chdir(dir_path)

        wallet_path = args[0]
        target_user = args[1]
        url_version = args[2]    
        target_id = args[3]    
        domain = args[4] 
        
        self_id = None
        jsonOutputOnly = False
        for i in (5,6):
            if len(args) >= i+1:
                if args[i] == 'json':
                    jsonOutputOnly = True
                else:
                    if self_id == None:
                        self_id = args[i]
        password = decelium.getpass(wallet_path)

 
        original_stdout = sys.stdout
        if jsonOutputOnly:
            sys.stdout = open("/dev/null","w")

        
        [pq,api_key,wallet] = self._load_pq(wallet_path,password,url_version,target_user)
        secret_passcode = wallet.get_secret(target_user, 'decelium_com_dns_code')
        #print(secret_passcode)
        if 'error' in secret_passcode:
            return secret_passcode
        
        sys.stdout = original_stdout
        dns_id = self.deploy_dns(pq,api_key,domain,target_id,secret_passcode)
        original_stdout = sys.stdout
        if jsonOutputOnly:
            sys.stdout = open("/dev/null","w")        
        #print("dns_id ..."+str(dns_id))
        return json.dumps(dns_id)
            
if __name__ == "__main__":
    # if you import as a library, then the importer is in charge of these imports
    direc = '/'.join(__file__.split('/')[:-3]) +'/'
    #os.chdir(direc)
    #sys.path.append('./')
    from decelium_wallet.crypto import crypto
    from decelium_wallet import decelium
    c = Deploy()
    c.run(*sys.argv[1:])

    
def run(*args):
    c = Deploy()
    return c.run (args)