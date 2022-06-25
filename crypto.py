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
    def do_encode_string(obj):
        string = jsondateencode_crypto.dumps(obj,separators=(',', ':'))
        encoded = base64.b64encode(string.encode('ascii'))
        return encoded.decode('ascii') 

    def do_decode_string(data_packet):
        user_data_dev = base64.b64decode(data_packet) 
        data2 = jsondateencode_crypto.loads(user_data_dev.decode("ascii"))
        return data2
    
    # TODO break into crypto modules and support various versions
    def generate_user(version='python-ecdsa-0.1'):
        assert version == "python-ecdsa-0.1"
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256) 
        vk = sk.get_verifying_key()
        user = {'api_key':vk.to_string().hex(),
                'private_key':sk.to_string().hex(),
                'version':"python-ecdsa-0.1"}
        return user

    def generate_user_from_string(private_key,version='python-ecdsa-0.1'):
        assert version == "python-ecdsa-0.1"
        #cls, string, curve=NIST192p, hashfunc=sha1):        
        pk = binascii.unhexlify(private_key)
        sk = ecdsa.SigningKey.from_string(pk,hashfunc=hashlib.sha256,curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        user = {'api_key':vk.to_string().hex(),
                'private_key':sk.to_string().hex(),
                'version':"python-ecdsa-0.1"}
        return user

    def sign_request(msg,signers,version='python-ecdsa-0.1'):
        assert version == "python-ecdsa-0.1"
        q = crypto.do_encode_string(msg)
        msg = msg.copy()
        sigs = {}
        for signer in signers:
            pk = binascii.unhexlify(signer['private_key'])
            sk = ecdsa.SigningKey.from_string(pk,hashfunc=hashlib.sha256,curve=ecdsa.SECP256k1)
            sigs[signer['api_key']] = sk.sign(q.encode()).hex()
        msg['__sigs'] = sigs
        return msg

    def verify_request(msg,version='python-ecdsa-0.1'):
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
            
        return msg   


    def decode(payload,password,version='python-ecdsa-0.1'): 
        assert version == "python-ecdsa-0.1"
        q= hashlib.sha224(password.encode('utf-8')).hexdigest()[:32]
        key = base64.urlsafe_b64encode(str.encode(q))
        f = Fernet(key)
        return f.decrypt(str.encode(payload)).decode()

    def encode(content,password,version='python-ecdsa-0.1'): 
        assert version == "python-ecdsa-0.1"
        q= hashlib.sha224(password.encode('utf-8')).hexdigest()[:32]
        key = base64.urlsafe_b64encode(str.encode(q))
        f = Fernet(key)
        token = f.encrypt(str.encode(content))
        return token.decode()
    
    def encode_key(content,password,version='python-ecdsa-0.1'): 
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
        return token.decode(),key.decode()    
    
    def decode_key(payload,password,key,version='python-ecdsa-0.1'): 
        assert version == "python-ecdsa-0.1"
        password = password.encode('utf-8')
        key = key.encode('utf-8')
        f = Fernet(key)
        data = f.decrypt(str.encode(payload))
        return data.decode()           
