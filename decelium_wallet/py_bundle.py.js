export default `
import ecdsa
import sys,binascii
from cryptography.fernet import Fernet
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib, json
import datetime
import getpass



class jsondateencode_crypto:
    def loads(dic):
        return json.loads(dic,object_hook=datetime_parser)
    def dumps(dic,separators=(',', ':')):
        return json.dumps(dic,default=datedefault,separators=separators)

def datedefault(o):
    if isinstance(o, tuple):
        l = ['__ref']
        l = l + o
        return l
    if isinstance(o, (datetime.date, datetime.datetime,)):
        return o.isoformat()
    
def datetime_parser(dct):
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
    for k, v in dct.items():
        if isinstance(v, str) and "T" in v:
            try:
                dct[k] = datetime.datetime.strptime(v, DATE_FORMAT)
            except:
                pass
    return dct

class crypto:
    @staticmethod
    def getpass(format=None,rootfile=None):
        #if file != None:
        #    return wallet.getpass(rootfile)
        raise Exception("Deprecated. Use wallet.discover instead. It is more secure.")
        path = ''
        password = None
        while password == None and len(path)<=3*4: 
            try:
                with open(path+'.password','r') as f:
                    password =  f.read()
                    return password.strip()
            except:
                path = path + '../'
                password = None
        ret = getpass.getpass()
        if format == 'json':
            ret = json.dumps(ret)
        return ret

    @staticmethod
    def do_encode_string(obj,format=None):
        string = jsondateencode_crypto.dumps(obj,separators=(',', ':'))
        encoded = base64.b64encode(string.encode('ascii'))
        if format == 'json':
            return json.dumps(encoded.decode('ascii'))
        return encoded.decode('ascii') 

    @staticmethod
    def do_decode_string(data_packet,format=None):
        user_data_dev = base64.b64decode(data_packet) 
        data2 = jsondateencode_crypto.loads(user_data_dev.decode("ascii"))
        if format == 'json':
            data2 = json.dumps(data2)
        return data2
    
    # TODO break into crypto modules and support various versions
    @staticmethod
    def generate_user(version='python-ecdsa-0.1',format=None):
        assert version == "python-ecdsa-0.1"
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256) 
        vk = sk.get_verifying_key()
        pk = vk.to_string().hex()
        user = {'api_key':pk,
                'address':pk[-42],
                'private_key':sk.to_string().hex(),
                'version':"python-ecdsa-0.1"}
        if format == 'json':
            user = json.dumps(user)
        return user

    @staticmethod
    def generate_user_from_string(private_key,version='python-ecdsa-0.1',format=None):
        assert version == "python-ecdsa-0.1"
        #cls, string, curve=NIST192p, hashfunc=sha1):        
        try:
            pk = binascii.unhexlify(private_key)
            sk = ecdsa.SigningKey.from_string(pk,hashfunc=hashlib.sha256,curve=ecdsa.SECP256k1)
            vk = sk.get_verifying_key()
            user = {'api_key':vk.to_string().hex(),
                    'address':vk.to_string().hex()[-42],
                    'private_key':sk.to_string().hex(),
                    'version':"python-ecdsa-0.1"}
        except:
            import traceback as tb
            exc = tb.format_exc()
            user = {"error":"error reading private key:"+ exc}
        if format == 'json':
            user = json.dumps(user)
        return user

    @staticmethod
    def sign_request(msg,signers,version='python-ecdsa-0.1',format=None):
        assert version == "python-ecdsa-0.1"
        q = crypto.do_encode_string(msg)
        msg = msg.copy()
        sigs = {}
        for signer in signers:
            pk = binascii.unhexlify(signer['private_key'])
            sk = ecdsa.SigningKey.from_string(pk,hashfunc=hashlib.sha256,curve=ecdsa.SECP256k1)
            sigs[signer['api_key']] = sk.sign(q.encode()).hex()
        msg['__sigs'] = sigs
        if format == 'json':
            msg = json.dumps(msg)        
        return msg

    @staticmethod
    def verify_request(msg,version='python-ecdsa-0.1',format=None):
        assert version == "python-ecdsa-0.1"
        verified = {}
        msg = msg.copy()
        msg_to_verify = msg.copy()
        del(msg_to_verify['__sigs'])
        q = crypto.do_encode_string(msg_to_verify)
        for public_key in msg['__sigs']:
            try:
                sig =msg['__sigs'][public_key]
                pk = binascii.unhexlify(public_key)
                vk = ecdsa.VerifyingKey.from_string(pk,hashfunc=hashlib.sha256, curve=ecdsa.SECP256k1 )# hashfunc=sha256 # the default is sha1
                verified[public_key] =vk.verify(binascii.unhexlify(sig), q.encode())
            except:
                verified[public_key] =False

        msg['__verified_list'] = verified
        try:
            msg['api_key_verified'] = verified[msg['api_key']]
        except:
            msg['api_key_verified'] = False
        if format == 'json':
            msg = json.dumps(msg)              
        return msg   

    @staticmethod
    def decode(payload,password,version='python-ecdsa-0.1',format=None): 
        assert version == "python-ecdsa-0.1"
        q= hashlib.sha224(password.encode('utf-8')).hexdigest()[:32]
        key = base64.urlsafe_b64encode(str.encode(q))
        f = Fernet(key)
        dec = f.decrypt(str.encode(payload)).decode()
        if format == 'json':
            dec = json.dumps(dec)          
        return dec
            
    @staticmethod
    def encode(content,password,version='python-ecdsa-0.1',format=None): 
        assert version == "python-ecdsa-0.1"
        q= hashlib.sha224(password.encode('utf-8')).hexdigest()[:32]
        key = base64.urlsafe_b64encode(str.encode(q))
        f = Fernet(key)
        token = f.encrypt(str.encode(content))
        enc = token.decode()
        if format == 'json':
            enc = json.dumps(enc)        
        return enc
    
    @staticmethod
    def encode_key(content,password,version='python-ecdsa-0.1',format=None): 
        assert version == "python-ecdsa-0.1"
        password = password.encode('utf-8')
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        f = Fernet(key)
        token = f.encrypt(content.encode('utf-8'))    
        ret = (token.decode(),key.decode())
        if format == 'json':
            ret = json.dumps(ret)
        return ret
    
    @staticmethod
    def decode_key(payload,password,key,version='python-ecdsa-0.1',format=None): 
        assert version == "python-ecdsa-0.1"
        password = password.encode('utf-8')
        key = key.encode('utf-8')
        f = Fernet(key)
        data = f.decrypt(str.encode(payload))
        dec = data.decode()
        if format == 'json':
            dec = json.dumps(dec)
        return dec
from pathlib import Path
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
