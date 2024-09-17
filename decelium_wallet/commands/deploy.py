#contract=Deploy
#version=0.1

import os
import sys,json
 
sys.path.append('../../')
sys.path.append('../../../')

original_stdout = sys.stdout
sys.stdout = open(os.devnull,"w")
try:
    # Default to the locally installed wallet
    import decelium_wallet.decelium as decelium
    from decelium_wallet.crypto import crypto
    from decelium_wallet.chunk import Chunk
    from decelium_wallet.core import core
except:        
    # Otherwise use the pip package
    from decelium_wallet.crypto import crypto
    from decelium_wallet.chunk import Chunk
    import decelium_wallet.decelium as decelium
    from decelium_wallet.core import core

sys.stdout = original_stdout

import uuid
import base64
import pprint
import shutil     
import json
import time

def run(*args):
    c = Deploy()
    result=c.run(*args) 
    return result
    
class Deploy():
    def _load_pq(self,path,password,url_version,target_user):
        dw = decelium.SimpleWallet()

        dw.load(path,password)
        accts = dw.list_accounts()
        
        print("-----accts-----", accts)
        print(dw.get_user('admin'))
        
        assert target_user in accts
        user = dw.get_user(target_user)
        print("----user----", user)
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

    def _deploy_website(self,pq,dw,api_key,path,name,source_path,self_id,jsonOutputOnly,version):
    
        original_stdout = sys.stdout
        
        if jsonOutputOnly:
            sys.stdout = open(os.devnull,"w")
        #original_stdout = sys.stdout 
        from_path = source_path
        chunk_path = "remote_test"
        remote_path_ipfs = path
     
        remote=True

        
        del_fil = pq.delete_entity({'api_key':api_key, 'path':remote_path_ipfs, 'name':name}, remote=True, show_url=True)
        
        try:
            assert del_fil == True or 'error' in del_fil
        except:
            try:
                if 'message' in del_fil:
                    print("Could not complete delete fast enough... retry...")
                    time.sleep(10)
                    del_fil = pq.delete_entity({'api_key':api_key, 'path':remote_path_ipfs, 'name':name}, remote=True, show_url=True)
                assert del_fil == True or 'error' in del_fil
            except:
                print("Could not remove old file...")
                print("-------")
                print(del_fil)
                print("-------")
                print("END")
            
        assert del_fil == True or 'error' in del_fil
        if version == 'dev':
            connection_settings = {
                'host': '35.167.170.96',
                'port': 5001,
                'protocol': 'http',
            }
        elif version == 'test':
            connection_settings = {
                'host': '54.184.193.202',
                'port': 5001,
                'protocol': 'http',
            }
        elif version == 'mainnet':
            connection_settings = {
                'host': '35.161.106.244',
                'port': 5001,
                'protocol': 'http',
            }
        else:
            raise Exception("Could not find IPFS server for upload")
        
        dist_list = self.core.net.create_ipfs({
            'api_key':api_key,
            'file_type':'ipfs',
            'connection_settings':connection_settings,
            'payload_type':'local_path',
            'payload':from_path
        }, remote=True, show_url=True)
        
        
        for item in dist_list:
            if item['name'] == 'quickstart/index.html':
                item['root'] = True
                break  

        print("-----dist_list-----", dist_list)
    
        q = {
            'api_key':api_key,
            'path':remote_path_ipfs,
            'name':name,
            'file_type':'ipfs',
            'payload_type':'ipfs_pin_list',
            'payload':dist_list
        }

        
        fil  = pq.create_entity(q, remote=True)
        print("------fil------", fil)
        
        if 'message' in fil and fil['message']=='Endpoint request timed out':
            time.sleep(5)
            for i in range (1,5):
                print("uploading . . . "+str(i)+"/5")
                data_test  = pq.download_entity({'api_key':api_key,'path':remote_path_ipfs+"/"+name , 'attrib':True},remote=True)
                print("---data_test---", data_test)
                if not 'self_id' in data_test: 
                    time.sleep(i*5)
                else:
                    fil = data_test['self_id']
                    break
        print("later upload response...  ",fil)
        assert 'obj-' in fil
        data  = pq.download_entity({'api_key':api_key,'self_id':fil , 'attrib':True},remote=True)
        
        assert 'obj-' in fil
        return fil
    
      
    
    def _deploy_small_website(self,pq,api_key,path,name,source_path,self_id,jsonOutputOnly):
        shutil.make_archive('temp_upload', 'zip', source_path)
        with open("temp_upload.zip",'rb') as f:
            bts = f.read()
            encoded = base64.b64encode(bts).decode("ascii") 
            
        original_stdout = sys.stdout
        if jsonOutputOnly:
            sys.stdout = open(os.devnull,"w")
            
        #print("encoded...  ", encoded[0:20])
        remote=True
        fil  = pq.delete_entity({'api_key':api_key, 
                                'path':path, 
                                'name':name, 
                                },remote=remote) # show_url=True to debug
        #print(fil)                            
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
        #print("upload response...  ",fil)
        sys.stdout = original_stdout        
        assert 'obj-' in fil
        data  = pq.download_entity({'api_key':api_key,'self_id':fil , 'attrib':True},remote=remote)
        #import pprint
        #pprint.pprint(data)
        #print(json.dumps(data))
        return fil
        #print("Uploaded to "+fil)

    def get_password(wallet_path):
        password = decelium.getpass(wallet_path)
        #print("password="+str(password))
        return password

    def explain(self):
        return "wallet_path url_version site_dir dec_path"

    def run(self,args):
        print("IN DEPLOY!")
        wallet_path = args[0]
        target_user = args[1]
        url_version = args[2]    
        site_dir = args[3]    
        upload_dir = args[4] 
        dns_host = None
        dns_secret_location = None
        version = None
        if 'dev' in url_version:
            version = 'dev'
        if 'test' in url_version:
            version = 'test'
        if 'mainnet' in url_version:
            version = 'mainnet'
        if not version:
            raise Exception("Could not detect upload version as dev or test")
        
        self.core = core()
        
        print("----site_dir----", site_dir)
        
        if len(args) >= 6 and len(args[5]) > 5:
            dns_host = args[5]
        if len(args) >= 7 and len(args[6]) > 4:
            dns_secret_location = args[6]
        if not dns_host and dns_secret_location:
            print("If you provide a dns_host you need to specify where the secret is located within your wallet as well")
        #print("dns_host",args)
        self_id = None
        jsonOutputOnly = False
        for i in (5,6,7,8):
            if len(args) >= i+1:
                if args[i] == 'json':
                    jsonOutputOnly = True
                else:
                    if self_id == None:
                        self_id = args[i]
        password = decelium.getpass(wallet_path)
    
        with open(wallet_path) as f:
            wallet_data = f.read() 
        # raw_wallet = self.load_wallet_strings_from_disk()
        success = self.core.load_wallet(data=wallet_data, password=password)
        print("CONNECTING TO "+ url_version)
        self.core.initial_connect(target_url=url_version, target_user="admin")
    
        #---- begin
        #root_path= site_dir
        #site_name = upload_dir.split("/")[-1]
        #website_path = '/'.join(upload_dir.split("/")[:-1])
        root_path='/'.join(site_dir.split("/")[:-1])
        site_name = site_dir.split("/")[-1]
        #website_path = '/'.join(upload_dir.split("/")[:-1])
        website_path = upload_dir
        original_stdout = sys.stdout
        #if jsonOutputOnly:
        #    sys.stdout = open(os.devnull,"w")

        #print(root_path)
        #print(site_name)
        #print(website_path)
        #return
        
        print("-----root_path-----",root_path)
        print("-----site_name-----",site_name)
        
        [pq,api_key,wallet] = self._load_pq(wallet_path,password,url_version,target_user)
        secret_passcode = wallet.get_secret(target_user, dns_secret_location)
        print("Deploying")
        sys.stdout = original_stdout
        website_id = self._deploy_website(pq, wallet, api_key, root_path, site_name, website_path, self_id, jsonOutputOnly,version)
        original_stdout = sys.stdout
        if jsonOutputOnly:
            sys.stdout = open(os.devnull,"w")        
        
        dns = ""
        #print("deploy_website ..."+website_id)
        if dns_host: #(self,       pq,api_key,path,    name,    secret_passcode):
            dns = self._deploy_dns(pq,api_key,'/_dns/',dns_host,website_id,secret_passcode)
            #print("deploy_dns ..."+ str(dns))
        else:        
            pass
            #print("skip_dns ...")
        
        lst= pq.list({'api_key':api_key, 'path':root_path, },remote=True)
        sys.stdout = original_stdout
        return json.dumps({"app_id":website_id,"dns_id":dns,"list":lst})
    
if __name__ == "__main__":
    direc = '/'.join(__file__.split('/')[:-3]) +'/'

    run(*sys.argv[1:])
    print("finished. Waiting . . .")
    time.sleep(10)
    
def run(*args):
    c = Deploy()
    return c.run (args)