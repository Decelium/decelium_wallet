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
        dns_name = args['dns_name']
        target_id = args['target_id']
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
                                    'path':'/_dns/'+dns_name,'name':dns_name},[target_user]))
        del_fil = decw.net.delete_entity(decw.dw.sr({'api_key':decw.dw.pubk(), 
                                    'path':'/_dns/'+dns_name},[target_user]))
        assert del_fil == True or 'error' in del_fil, "Could not remove old file"
        if 'remove' in args and args['remove'] != None:
            return del_fil
        secret_passcode = decw.dw.get_secret(target_user, 'decelium_com_dns_code')

        if 'error' in secret_passcode:
            return secret_passcode
        signed_upload = decw.dw.sr({'api_key':decw.dw.pubk(),
                                'path':'/_dns/'+dns_name,
                                'name':dns_name,
                                'file_type':'host',
                                'attrib':{'host':dns_name,
                                            'secret_password':secret_passcode,
                                            'target_id':target_id}
                                })
    
        fil  = decw.net.create_entity(signed_upload)
        assert 'obj-' in fil
        return fil        