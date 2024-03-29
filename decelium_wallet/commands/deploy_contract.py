#contract=Deploy
#version=0.1

import os
import sys
 
sys.path.append('../../')
sys.path.append('../../../')

original_stdout = sys.stdout
sys.stdout = open("/dev/null","w")
from decelium.crypto import crypto
from decelium import decelium
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

    def _deploy_dns(self,pq,api_key,path,name,website_id,secret_passcode):
        remote=True
        for item in pq.list({'api_key':api_key, 'attrib':{'host':name}, },remote=True): 
            print("REMOVING "+str(item))   
            fil  = pq.delete_entity({'api_key':api_key, 
                                    'self_id':item['self_id'], 
                                    },remote=remote) # show_url=True to debug
            
        fil  = pq.delete_entity({'api_key':api_key, 
                                'path':path, 
                                'name':name, 
                                },remote=remote) # show_url=True to debug

        try:
            print("delete"+fil)             
        except:
            pass               
        assert fil == True or 'error' in fil
        res_url =pq.create_entity({'api_key':api_key,
                                'path':path,
                                'name':name,
                                'file_type':'host',
                                'attrib':{'host':name,
                                            'secret_password':secret_passcode,
                                            'target_id':website_id}        
                                  },remote=remote)
        try:
            assert 'obj-' in res_url
        except:
            print("Could not set up dns")
            print(res_url)
        return res_url

    def _deploy_website(self,pq,api_key,path,name,source_path,self_id,jsonOutputOnly):
        from decelium.chunk import Chunk

        original_stdout = sys.stdout
        if jsonOutputOnly:
            sys.stdout = open("/dev/null","w")
            
        print(dir(Chunk))

        from_path = source_path
        chunk_path = "remote_test"
        remote_path_ipfs = path
     
        remote=True
        dir_fil = Chunk.upload(pq,api_key,remote,from_path,chunk_path)

        print({'api_key':api_key,'path':remote_path_ipfs,'name':name,})
        del_fil  = pq.delete_entity({'api_key':api_key,'path':remote_path_ipfs,'name':name,},remote=True)
        print(del_fil)
        print({
            'api_key':api_key,
            'path':remote_path_ipfs,
            'name':name,
            'file_type':'ipfs',
            'payload_type':'chunk_directory',
            'payload':dir_fil})
        
        q = {
            'api_key':api_key,
            'path':remote_path_ipfs,
            'name':name,
            'file_type':'ipfs',
            'payload_type':'chunk_directory',
            'payload':dir_fil}
        
        fil  = pq.create_entity(q,remote=True)
        #print(fil['traceback'])
        print("early upload response...  ",fil)
        if 'message' in fil and fil['message']=='Endpoint request timed out':
            time.sleep(5)
            for i in range (1,5):
                data_test  = pq.download_entity({'api_key':api_key,'path':remote_path_ipfs+"/"+name , 'attrib':True},remote=True)
                if not 'self_id' in data_test: 
                    time.sleep(i)
                else:
                    fil = data_test['self_id']
                    break
        print("later upload response...  ",fil)
        assert 'obj-' in fil
        data  = pq.download_entity({'api_key':api_key,'self_id':fil , 'attrib':True},remote=True)
        sys.stdout = original_stdout 
        print(json.dumps(data))
        return fil
    
    def _deploy_small_website(self,pq,api_key,path,name,source_path,self_id,jsonOutputOnly):
        shutil.make_archive('temp_upload', 'zip', source_path)
        with open("temp_upload.zip",'rb') as f:
            bts = f.read()
            encoded = base64.b64encode(bts).decode("ascii") 
            
        original_stdout = sys.stdout
        if jsonOutputOnly:
            sys.stdout = open("/dev/null","w")
            
        print("encoded...  ", encoded[0:20])
        remote=True
        fil  = pq.delete_entity({'api_key':api_key, 
                                'path':path, 
                                'name':name, 
                                },remote=remote) # show_url=True to debug
        print(fil)                            
        assert fil == True or 'error' in fil

        fil_args = {
            'api_key':api_key,
            'path':path,
            'name':name,
            'file_type':'ipfs',
            'payload_type':'folder',
            'payload':encoded}
        if self_id != None:
            fil_args['self_id'] = self_id    

        fil  = pq.create_entity(fil_args,remote=remote)
    
        #print(fil['traceback'])
        print("upload response...  ",fil)
        sys.stdout = original_stdout        
        assert 'obj-' in fil
        data  = pq.download_entity({'api_key':api_key,'self_id':fil , 'attrib':True},remote=remote)
        #import pprint
        #pprint.pprint(data)
        print(json.dumps(data))
        return fil
        print("Uploaded to "+fil)

    def get_password(wallet_path):
        password = decelium.getpass(wallet_path)

    def __deploy_contract(self,pq,api_key,path,name,target_contract_id,target_contract_path):    
        with open(target_contract_path,'r') as contract_py:
            func_data= contract_py.read()
        
        
        remote=True
        full_path =path+name 
        #print(api_key)
        fil  = pq.delete_entity({'api_key':api_key, 
                                'path':path, 
                                'name':name, 
                                },remote=remote) # show_url=True to debug
        assert fil == True or 'error' in fil
        if target_contract_id:
            fil  = pq.delete_entity({'api_key':api_key, 
                                    'self_id':target_contract_id, 
                                    },remote=remote) # show_url=True to debug
        assert fil == True or 'error' in fil
        
        fil  = pq.create_entity({'api_key':api_key, 
                                'path':path, 
                                'name':name, 
                                'self_id':target_contract_id, 
                                'file_type':'file',
                                'payload':func_data
                                },remote=remote) # show_url=True to debug
        if 'traceback' in fil:
            pprint.pprint(fil['traceback'])
        if 'error' in fil:
            pprint.pprint(fil['error'])

        assert 'obj-' in fil
        print("launched "+fil)
        return fil


    def explain(self):
        return "wallet_path target_user url_version site_dir upload_dir target_contract_id"
         
    def run(self,*args):
        dir_path = os.path.dirname(os.path.realpath(__file__))    
        os.chdir(dir_path)
        wallet_path = args[0]
        target_user = args[1]
        url_version = args[2]    
        site_dir = args[3]    
        upload_dir = args[4] 
        if len(args) > 5:
            target_contract_id = args[5] 
        else:
            target_contract_id = None
        jsonOutputOnly = False

        for i in (5,6,7,8):
            if len(args) >= i+1:
                if args[i] == 'json':
                    jsonOutputOnly = True
        
        password = decelium.getpass(wallet_path)
    
        root_path='/'.join(site_dir.split("/")[:-1])
        site_name = site_dir.split("/")[-1]
        #target_contract_path = '/'.join(upload_dir.split("/")[:-1])
        target_contract_path = upload_dir
 
        original_stdout = sys.stdout
        if jsonOutputOnly:
            sys.stdout = open("/dev/null","w")

        print(root_path)
        print(site_name)
        print(target_contract_path)
        [pq,api_key,wallet] = self._load_pq(wallet_path,password,url_version,target_user)

        sys.stdout = original_stdout
        # _deploy_website(pq,api_key,root_path,site_name,website_path,self_id,jsonOutputOnly)
        contract_id = self.__deploy_contract(pq,api_key,root_path,site_name,target_contract_id,target_contract_path)
        original_stdout = sys.stdout
        if jsonOutputOnly:
            sys.stdout = open("/dev/null","w")        
        
        print("deploy_contract ..."+contract_id)
        
        for item in pq.list({'api_key':api_key, 'path':root_path, },remote=True):
            print("deployed... ", item['self_id'], ' as ', item['dir_name'])
        sys.stdout = original_stdout 
            
if __name__ == "__main__":
    # if you import as a library, then the importer is in charge of these imports
    direc = '/'.join(__file__.split('/')[:-3]) +'/'
    #os.chdir(direc)
    #sys.path.append('./')
    from decelium.crypto import crypto
    from decelium import decelium
    c = Deploy()
    c.run(*sys.argv[1:])

def run(*args):
    c = Deploy()
    return c.run (args)