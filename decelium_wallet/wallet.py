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
    """ 
    def load(self,password=None,data=None,wallet=None,format=None):
        if wallet and type(data) == dict:
            self.wallet = wallet
            if format == 'json':
                return json.dumps(True)
            return True
        if data == None:
            self.wallet = {}
            if format == 'json':
                return json.dumps(True)
            return True
        if password != None:
            astr = crypto.decode(astr,password,version='python-ecdsa-0.1')
        else:
            astr = data
        self.wallet= crypto.do_decode_string(astr )
        if format == 'json':
            return json.dumps(True)

    def export(self,password=None,wallet=False,format=None):
        if wallet == True:
            return wallet.copy()
        dumpstr = crypto.do_encode_string(self.wallet)
        if password != None:
            dumpstr = crypto.encode(dumpstr,password,version='python-ecdsa-0.1')
        return dumpstr
    """
    def __init__(self,mode="fs",fs=None):
        self.mode=mode
           
    def load(self,path=None,password=None,data=None):
        if self.mode=="fs":
            self.load_fs(path,password,data)
        else:
            self.load_js(path,password,data)
        
    def save(self,path,password=None):
        if self.mode=="fs":
            self.save_fs(path,password)
        else:
            self.save_js(path,password)        
                
    def load_js(self,path=None,password=None,data=None):
        self.wallet={};
    
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
    
    def request_sign(self,message,format=None):
        '''
            Request a signature on a message from the user.
        '''
        print("Authorizing message")
        if format == 'json':
            return json.dumps(True)
        return True

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