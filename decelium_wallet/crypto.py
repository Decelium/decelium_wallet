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