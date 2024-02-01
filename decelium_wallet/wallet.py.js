export default `from pathlib import Path
if not "crypto" in globals():   
    try:
        from .crypto import crypto
    except:
        import crypto
        crypto = crypto.crypto
        #from decelium.crypto import crypto
import json
import os,sys
from os.path import exists
from cryptography.fernet import InvalidToken

class wallet():
    def __init__(self):
        self.wallet = {}
        pass
    def load(self,path=None,password=None,data=None,format=None,mode='fs'):
        if path == None and data != None:
            mode = 'js'
        try:
            if mode=="fs":
                return self.load_fs(str(path),password,data)
            else:
                return self.load_js(str(path),password,data)
        except InvalidToken:
            return False
        
    def save(self,path,password=None,mode='fs'):
        if mode=="fs":
            return self.save_fs(path,password)
        else:
            return self.save_js(path,password)        
                
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
        return True
        
    
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
            return True
        return False
    
    def export_encrypted(self,password=None):
        dumpstr = crypto.do_encode_string(self.wallet)
        if password != None:
            dumpstr = crypto.encode(dumpstr,password,version='python-ecdsa-0.1')
        return dumpstr
        
    def save_fs(self,path,password=None):
        if exists(path):
            os.remove(path)
        dumpstr = self.export_encrypted(password)
        with open(path,'w') as f:
            f.write(dumpstr)
            
        with open(path,'r') as f:
            savedstr = f.read()
            assert dumpstr == savedstr
        return True
            
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


    def create_account(self,user ,label,version='python-ecdsa-0.1',format=None):
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
        #user["some_data"] = "return"
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

        if sys.getsizeof(a_string) > 1024/2:
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
        return crypto.generate_user_from_string(private_key=private_key,version='python-ecdsa-0.1',format=format)
    
    @staticmethod
    def getpass(walletpath):
        wallet_path = Path(walletpath)
        wallet_dir = wallet_path.parent
        # look for a properly named .filename.dec.password
        password_file = wallet_dir / (wallet_path.stem + '.dec.password')
        if not password_file.is_file():
            # then look for a .password
            password_file = wallet_dir / '.password'
            if not password_file.is_file():
                # use discover to find the password file
                current_dir = Path(__file__).parent
                wallet_infos = wallet.discover(current_dir)
                for info in wallet_infos:
                    if info['wallet'] == str(wallet_path):
                        password_file = Path(info['passfile'])
                        break
                else:
                    raise FileNotFoundError("Password file not found.")

        # read the password from the file
        with password_file.open('r') as f:
            password = f.read().strip()

        return password        
        
    @staticmethod
    def discover(root="./", password=None):
        root = Path(root)
        original_root = root
        wallet_infos = []

        for depth in range(8):
            current_dir = root.absolute()

            # Check for all .dec files (potential wallets)
            for file in current_dir.glob('*.dec'):
                password_file = current_dir / (file.stem + '.dec.password')
                if not password_file.is_file():
                    password_file = current_dir / (file.stem + '.password')

                wallet_info = {
                    'wallet': str(file),
                    'passfile': str(password_file) if password_file.is_file() else None
                }

                if password is not None:
                    w = wallet()
                    try:
                        wallet_info['can_decrypt'] = w.load(file, password)
                    except InvalidToken:
                        wallet_info['can_decrypt'] = False

                wallet_infos.append(wallet_info)

            root = current_dir.parent  # Move up one directory level

        root = original_root  # Reset root to the original directory

        # Only look for orphaned password files if no password was provided
        if password is None:
            for depth in range(8):
                current_dir = root.absolute()

                # Check for all .password files (potential orphaned password files)
                for password_file in current_dir.glob('*.password'):
                    if password_file.stem:  # Exclude files literally named ".password"
                        wallet_file = current_dir / password_file.stem
                        if not wallet_file.with_suffix('.dec').is_file():
                            wallet_infos.append({
                                'wallet': None,
                                'passfile': str(password_file)
                            })

                root = current_dir.parent  # Move up one directory level

        return wallet_infos
`;
