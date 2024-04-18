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
import json
    
class Deploy():
    def exec(self,args):
        target_user = args['target_user']
        decelium_path = args['decelium_path']
        local_path = args['local_path']
        wallet_path = args['wallet_path']
        node_url = args['node_url']

        decw = core()
        with open(wallet_path,'r') as f:
            data = f.read()
        with open(wallet_path+".password",'r') as f:
            password = f.read()
        loaded = decw.load_wallet(data,password)
        assert loaded == True
        connected = decw.initial_connect(target_url=node_url,
                                        api_key=decw.dw.pubk())

        del_fil = decw.net.delete_entity(decw.dw.sr({'api_key':decw.dw.pubk(), 
                                    'path':decelium_path},[target_user]))
        if 'remove' in args and args['remove'] != None:
            return del_fil
        assert del_fil == True or 'error' in del_fil, "Could not remove old file"
        
        ipfs_connection_settings = {
            'host': 'devdecelium.com',
            'port': 5002,
            'protocol': 'https',
        }
        
        dist_list = decw.net.create_ipfs({
            'api_key':decw.dw.pubk(target_user),
            'file_type':'ipfs',
            'connection_settings':ipfs_connection_settings,
            'payload_type':'local_path',
            'payload':local_path
        })
        doc = {
            'api_key':decw.dw.pubk(target_user),
            'path':decelium_path,
            'file_type':'ipfs',
            'payload_type':'ipfs_pin_list',
            'payload':dist_list
        }        
        if 'target_id' in args and len(args['target_id'])  > 0:
            doc['self_id'] = args['target_id']

        fil  = decw.net.create_entity(decw.dw.sr(doc))
        assert 'obj-' in fil
        return fil        