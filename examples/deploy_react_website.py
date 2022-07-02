import sys
import pandas as pd
import unittest    
import json
sys.path.append('../../')
import pandas as pd
import requests
import datetime,time
import unittest
import uuid
import decelium.decelium as decelium
import decelium.crypto as crypto
from sys import getsizeof
from os.path import exists
import base64
import shutil


def upload_to_decelium(pq,api_key,site_name,source_path):
    shutil.make_archive('temp_upload', 'zip', source_path)
    with open("temp_upload.zip",'rb') as f:
        bts = f.read()
        encoded = base64.b64encode(bts).decode("ascii")       
    print("encoded...  ", encoded[0:20])
    path= '/example/'
    remote=True
    name =site_name+str(uuid.uuid4())+'.dat'

    fil  = pq.create_entity({
        'api_key':api_key,
        'path':'/my_websites/',
        'name':name,
        'file_type':'ipfs',
        'payload_type':'folder',
        'payload':encoded},remote=remote)
    #print(fil['traceback'])
    print("upload response...  ",fil)
    assert 'obj-' in fil
    data  = pq.download_entity({'api_key':api_key,'self_id':fil , 'attrib':True},remote=remote)
    import pprint
    pprint.pprint(data)
    return True
    print("Uploaded to "+fil)


def load_pq(path,password):
    dw = decelium.SimpleWallet()
    dw.load(path,password)
    accts = dw.list_accounts()
    assert 'admin' in accts
    print(dw.get_user('admin'))
    user = dw.get_user('admin')
    url_version = 'dev.paxfinancial.ai'
    pq_raw = decelium.Decelium(url_version=url_version,api_key=user['api_key'])
    pq = decelium.SimpleCryptoRequester(pq_raw,{user['api_key']:user})
    return pq,user['api_key']

if __name__ == "__main__":
    # example use: "python3 deploy_react_website.py wallet_password test_website /app/react-nft-boiler/website/build/"
    path = '../.wallet.dec'
    password = sys.argv[1:][0]
    site_name = sys.argv[1:][1]
    source_directory = sys.argv[1:][2]
    print("connect \n---------")
    [pq,api_key] = load_pq(path,password)
    print("upload \n---------")
    upload_to_decelium(pq,api_key,site_name,source_directory)
    
    '''
    # Create Site
    data  = pq.delete_entity({'api_key':user['api_key'],'path':'/html_files/'+'index.html'},remote=remote)
    res_obj =pq.create_entity({'api_key':user['api_key'],  'path':'/html_files/', 
                                'name':'index.html','file_type':'file', 
                                'payload':website,},remote=remote)

    res_data =pq.download_entity({'api_key':user['api_key'], 'path':'/html_files/index.html'},remote=remote)
    print(res_data)        
    assert website==res_data
    '''
    '''
    res_url =pq.create_entity({'api_key':api_key,
                                'path':'/apps/'+app_dir+'/domains/',
                                'name':domain,
                                'file_type':'host',
                                'attrib':{'host':domain,
                                            'secret_password':secret_password,
                                            'target_id':res_obj}
                            },remote=remote)
    
    print("4",res_url)
    assert 'obj-' in res_url
    return True
    '''
    #
