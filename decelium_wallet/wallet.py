try:
    from .crypto import crypto
except:
    import crypto
    crypto = crypto.crypto
    #from decelium.crypto import crypto
import json
import os
from os.path import exists

class wallet():
    def __init__(self,mode="fs",fs=None):
        self.mode=mode
           
    def load(self,path=None,password=None,data=None,format=None):
        if path == None and data != None:
            self.mode = 'js'
        
        if self.mode=="fs":
            return self.load_fs(path,password,data)
        else:
            return self.load_js(path,password,data)
        
    def save(self,path,password=None):
        if self.mode=="fs":
            self.save_fs(path,password)
        else:
            self.save_js(path,password)        
                
    def load_js(self,path=None,password=None,data=None):
        self.wallet={}
        if type(data) == dict:
            # Force validation via encoding
            astr = crypto.do_encode_string(data)
        elif '{' in data:
            astr = crypto.do_encode_string(json.loads(data))
        else:
            astr = data
        if password != None:
            astr = crypto.decode(astr,password,version='python-ecdsa-0.1')
        
        self.wallet= crypto.do_decode_string(astr )        
        if type(self.wallet) == dict:
            return True
        return False
    
    def save_js(self,path,password=None):
        print(self.wallet);
    
    def load_fs(self,path=None,password=None,data=None):
        self.wallet = {}
        if path != None or data !=None:
            if data == None:
                if not exists(path):
                    return
                with open(path,'r') as f:
                    astr = f.read()
            elif type(data) == dict:
                # Force validation via encoding
                astr = crypto.do_encode_string(data)
            else:
                astr = crypto.do_encode_string(json.loads(data))
            if password != None:
                astr = crypto.decode(astr,password,version='python-ecdsa-0.1')
            self.wallet= crypto.do_decode_string(astr )

    def save_fs(self,path,password=None):
        if exists(path):
            os.remove(path)

        with open(path,'w') as f:
            dumpstr = crypto.do_encode_string(self.wallet)
            if password != None:
                dumpstr = crypto.encode(dumpstr,password,version='python-ecdsa-0.1')

            f.write(dumpstr)
        with open(path,'r') as f:
            savedstr = f.read()
            assert dumpstr == savedstr
    def sr(self,q,user_ids,format=None):
        return self.sign_request(q,user_ids,format=format)
    
    def pubk(self,uid,format=None):
        user = self.wallet[uid]
        key_data = user['user']
        if format == 'json':
            res = json.dumps(key_data['api_key'])
        else:
            res = key_data['api_key']
        return res
    
    
    def sign_request(self,q,user_ids,format=None):
        '''
            Request a signature on a message from the user.
        '''
        if q == None:
            return {"error":"sign_request can not use empty query"}
            
        if not 'api_key' in q or q['api_key'] == None:
            return {"error":"cant sign without selected api_key"}
        if not 'ses-' in q['api_key']:
            signers = []
            for uid in user_ids:
                user = self.wallet[uid]
                key_data = user['user']
                signers.append(key_data)
            qsig = crypto.sign_request(q,signers)
        else:
            qsig = q
        if format == 'json':
            qsig = json.dumps(qsig)
        return qsig


    def create_account(self,user = None,label=None,version='python-ecdsa-0.1',format=None):
        if user == None:
            user = crypto.generate_user(version=version)
        assert 'api_key' in user
        assert 'private_key' in user
        assert 'version' in user
        account_data = {'user':user,
                        'title':user['api_key'],
                        'image':None,
                        'description':None,
                        'secrets':{},
                        'watch_addresses':[]}
        if label == None:
            label = user['api_key']
        self.wallet[label] = account_data
        user["some_data"] = "return"
        if format == 'json':
            user = json.dumps(user)
        return user

    def list_accounts(self,format=None):
        ret = list(self.wallet.keys())
        if format == 'json':
            ret = json.dumps(ret)
        return ret
    
    def rename_account(self,old_label,new_label,format=None):
        self.wallet[new_label] = self.wallet[old_label]
        del(self.wallet[old_label])
        
    def get_account(self,label,format=None):
        if not label in self.wallet:
            return {'error':'User is not in wallet manager'}
        return self.wallet[label] 

    def get_user(self,label,format=None):
        if not label in self.wallet:
            return {'error':'User is not in wallet manager'}
        return self.wallet[label]['user'] 

    def set_secret(self,label, sid, sjson,format=None):
        if not label in self.wallet:
            return {'error':'User is not in wallet manager'}
        try:
            a_string = crypto.do_encode_string(sjson)
        except:
            return {'error':'could not encode secret as json'}

        if getsizeof(a_string) > 1024/2:
            return {'error':'can not store a secret larger than 0.5kb'}

        self.wallet[label]['secrets'][sid] = sjson 
        return True
    
    def get_secret(self,label, sid,format=None):
        if not label in self.wallet:
            return {'error':'User is not registered'}
        if not sid in self.wallet[label]['secrets']:
            return {'error':'secret not saved'}
        return self.wallet[label]['secrets'][sid] 

    def list_secrets(self,label,format=None):
        if not label in self.wallet:
            return {'error':'User is not registered'}
        return list(self.wallet[label]['secrets'].keys()) 

    def get_raw(self,format=None):
        if format == 'json':
            return json.dumps(self.wallet)
        return self.wallet

    def recover_user(self,private_key,format=None):
        return crypto.generate_user_from_string(private_key,version='python-ecdsa-0.1')