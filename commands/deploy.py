import sys
 
sys.path.append('../../')

from decelium.crypto import crypto
from decelium import decelium
import uuid
import base64
import pprint
import shutil
import os 

target_user = 'sid' 

def load_pq(path,password,url_version):
    global target_user
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


def deploy_dns(pq,api_key,path,name,secret_passcode):
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
                                        'target_id':target_self_id}
                            },remote=remote)
    assert 'obj-' in res_url
    return res_url

def deploy_website(pq,api_key,path,name,source_path,self_id):
    shutil.make_archive('temp_upload', 'zip', source_path)
    with open("temp_upload.zip",'rb') as f:
        bts = f.read()
        encoded = base64.b64encode(bts).decode("ascii")       
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
    print(fil_args)
    
    fil  = pq.create_entity(fil_args,remote=remote)
    #print(fil['traceback'])
    print("upload response...  ",fil)
    assert 'obj-' in fil
    data  = pq.download_entity({'api_key':api_key,'self_id':fil , 'attrib':True},remote=remote)
    import pprint
    pprint.pprint(data)
    return fil
    print("Uploaded to "+fil)


def explain():
    return "wallet_path url_version site_dir dec_path"

def run(*args):
    dir_path = os.path.dirname(os.path.realpath(__file__))    
    os.chdir(dir_path)
    #url_version = 'test.paxfinancial.ai'
    print(type(args))
    print(args)
    print(type(args[0]))
    print(args[0])
    wallet_path = args[0]
    url_version = args[1]    
    site_dir = args[2]    
    upload_dir = args[3]
    self_id = None
    if len(args) >= 5:
        self_id = args[4]
    password = crypto.getpass()
   
    #---- begin
    root_path='/'.join(site_dir.split("/")[:-1])
    site_name = site_dir.split("/")[-1]
    website_path = '/'.join(upload_dir.split("/")[:-1])

    print(root_path)
    print(site_name)
    print(website_path)
    #return
    
    [pq,api_key,wallet] = load_pq(wallet_path,password,url_version)
    #secret_passcode = wallet.get_secret('admin', 'decelium_com_dns_code')
    website_id = deploy_website(pq,api_key,root_path,site_name,website_path,self_id)
    print("deploy_website ..."+website_id)
        
    #if selection == "dns":
    #    deploy_dns(pq,api_key,root_path,dns_name,website_id,secret_passcode)
    #    print("deploy_dns ...")
    
    for item in pq.list({'api_key':api_key, 'path':root_path, },remote=True):
        print("deployed... ", item['self_id'], ' as ', item['dir_name'])
    '''
        python3 deploy.py ../../.wallet.dec dev.paxfinancial.ai  dec_path01~
    '''
if __name__ == "__main__":
    run(*sys.argv[1:])
