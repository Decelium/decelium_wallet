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
'''
DeceliumAPI

A Collection of tools used by the public to interface with Decentralized Cloud services. 
Compatible with the HTTP and websockets format of the Decelium project.

Author: Justin Girard
Date: December 2016
Licence: MIT Licence. Free to expand on the work and distribute freely.
 -- TODO This connector is (a) old (b) battle hardened. It needs a refactor but it is also currently bulletproof. 
 -- TODO move whole client connector into open source and revise PaxFinancial naming
'''

import datetime
import datetime, uuid, sys,os
import zipfile
from os import listdir
from os.path import isfile, join
import pickle
import base64
import json
import datetime
import urllib.parse
import sys 
#from .crypto import crypto
if not "crypto" in globals():    
    try:
        from .crypto import crypto
    except:
        import crypto
        crypto = crypto.crypto
        #from decelium.crypto import crypto

if not "wallet" in globals():    
    try:    
        from .wallet import wallet
    except:
        import wallet
        wallet = wallet.wallet
    import os

try:
    from processingNetwork.ProcessingNode import ProcessingNode
    from processingNetwork.ProcessingNetwork import ProcessingNetwork
    from financialapi.APIConnection import LocalApiConn
    from financialapi.SystemComponents import AuthorizeSection
except:
    pass
    #print("local mode only")

import contextlib
import sys

try:
    len(PaxFinancialAPIEndpointRegistry)
except:
    PaxFinancialAPIEndpointRegistry = {}
def getpass(path):
    return wallet.getpass(path)

def time_print_init():
    '''
        time_print_init():
        time_print_start(label):
        time_print_end(label):
        time_list_print():
    '''
    global ti_list_watch,ti_list_total
    ti_list_watch = {}
    ti_list_total = {}

def time_print_start(label):
    global ti_list_watch,ti_list_total
    ti_list_watch[label] = time.time()
        
def time_print_end(label):
    global ti_list_watch,ti_list_total
    if not label in ti_list_total:
        ti_list_total[label] = 0
    if ti_list_watch[label] > 0:
        ti_list_total[label] = ti_list_total[label] + time.time() -  ti_list_watch[label] 
    ti_list_watch[label] = 0

def time_list_print():
    global ti_list_total
    import pprint
    pprint.pprint(ti_list_total)

class DummyFile(object):
    def write(self, x): pass

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    yield
    sys.stdout = save_stdout

class jsondateencode_local:
    def loads(dic):
        return json.loads(dic,object_hook=datetime_parser)
    def dumps(dic):
        return json.dumps(dic,default=datedefault)

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

def tdtodict(tdelta):
    '''
    Helper Function turn a timedelta into json so it can be serialized
    '''
    assert type(tdelta) == datetime.timedelta
    js_td = {
        '__day':tdelta.days,
        '__second':tdelta.seconds,
        '__microsecond':tdelta.microseconds,
    }
    return js_td  

def dicttotd(din):
    '''
    Helper Function turn a timedelta into json so it can be serialized
    '''
    assert type(din) == dict 
    assert '__day' in din
    td = datetime.timedelta(
        days = din['__day'],
        seconds = din['__second'],
        microseconds = din['__microsecond']
    )
    return td


import importlib
def localfindclass(type_or_string,module_string=None,context=None,reload=True):
        typeVar = type_or_string
        if isinstance(type_or_string, str):
            if module_string == None:
                if context:
                    typeVar = context[type_or_string]
                else:
                    typeVar = globals()[type_or_string]
            else:
                #print("(EXPENSIVE) paxdk.localfindclass > (type_or_string,module_string,reload):",type_or_string,module_string,reload)
                #print("(A)computationally expensive paxdk.localfindclass > ",module_string)
                moduleIn = importlib.import_module(module_string)
                if reload:
                    print("(B)computationally expensive paxdk.localfindclass > ",module_string)
                    importlib.reload(moduleIn)
                try:
                    typeVar = getattr(moduleIn ,type_or_string)
                except Exception as e:
                    print("PaxFinancialAPI Failure: Failing to find an attribute in the module. Below are the attributes of the model.")
                    import pprint
                    print(moduleIn)
                    print(type_or_string)
                    pprint.pprint(dir(moduleIn))
                    raise(e)
                    
        return typeVar

class paxqueryengine():
    def __init__(self):
        self.query_definitions= {}
        self.query_objects= {}
        self.query_output_id= {}
        self.query_input_id= {}
        self.query_full_path = {}
        
        self.source_map = {}
        #self.out_id_map = {}
        
        self.__settings = {}
        self.source = ''
        self.limit = ''
        self.conditions = []
        self.offset = ''
    def query_local(source_id,query,url_version='dev'):
        '''
            time_print_init()
            time_print_start(label)
            time_print_end(label)
            time_list_print()
         
        '''
        time_print_init("")
        time_print_start("query_local")
        try:
            a = paxqueryengine.mc
        except:
            paxqueryengine.mc = LocalApiConn()

        q = {}
        q['qtype'] = source_id
        quer = query
        q['__encoded_query'] = paxqueryengine.do_encode(quer)
        packet = {
            'url':'/data/query',
            'network':url_version,
            'arguments':q
        }
        time_print_start("query_local_core")
        res = paxqueryengine.mc.do_input(packet)
        time_print_end("query_local_core")
        try:
            dat = jsondateencode_local.loads(res['body'])
        except Exception as e :
            print(e)
            dat = r.text
        time_print_end("query_local")
        time_list_print()
        return dat
    
    def query_websocket(source_id,query,url_version='dev'):
        from websocket import create_connection
        if 'http' in url_version:
            host =  url_version.replace('https','')
            host = host.replace('http','')
            host = host.replace('://','')
        else:
            host = url_version+'.paxfinancial.ai'
        try:
            paxqueryengine.ws
        except:
            paxqueryengine.ws = {}
        if host not in paxqueryengine.ws:
            paxqueryengine.ws[host] = create_connection("ws://"+host+'/data/query')
        args = {}
        args['qtype'] = source_id
        args['__encoded_query'] = paxqueryengine.do_encode(query)
        args['host'] = host.split(':')[0]
        #args['url'] = '/data/query'
        try:
            paxqueryengine.ws[host].send(json.dumps(args))
            result =  paxqueryengine.ws[host].recv()
        except:
            paxqueryengine.ws[host].close()
            paxqueryengine.ws[host] = create_connection("ws://"+host+'/data/query')
            paxqueryengine.ws[host].send(json.dumps(args))
            result =  paxqueryengine.ws[host].recv()
            result = r'{}'.format(result)
            
        try:
            try:
                #print(result)
                #print(type(result))
                dat = jsondateencode_local.loads(result)
                if type(dat) == str:
                    dat = jsondateencode_local.loads(dat)
                #print('decoded 1 - ',dat)
                #print(type(dat))
            except Exception as e:
                print(e)
                pass
            if type(dat) == str and dat[0] in ['[','{']:
                dat = jsondateencode_local.loads(dat)
                #print(type(dat))
                #print('decoded 2 - ',dat)
        except Exception as e :
            print("DECODE ERROR")
            print(e)
            dat = r.text        
        return dat
    
    def query_remote(source_id,query,url_version='dev',show_url=False):
        import requests
        #url = 'https://g46w1ege85.execute-api.us-west-2.amazonaws.com/alpha/'+url_version+'/data/query'
        if 'http' in url_version:
            url = url_version+'/data/query'
        elif (url_version in ['dev','test','mainnet']):
            url = 'https://'+url_version+'.paxfinancial.ai/data/query'
        else:
            url = 'https://'+url_version+'/data/query'
        #print('requests',show_url)
        if show_url:
            print(url)
            print(query)
        data = {}
        data['qtype'] = source_id
        data['__encoded_query'] = paxqueryengine.do_encode(query)
        #print(url)
        r = requests.post(url, data = data)        
        try:
            #print(r.text)
            #print(type(r.text))
            dat = jsondateencode_local.loads(r.text)
            #print(dat)
        except Exception as e :
            print(e)
            dat = r.text
        return dat
    
    def query_prepare(source_id,query,url_version='dev'):
        #print('REMOTE' + url_version)
        import requests
        #url = 'https://g46w1ege85.execute-api.us-west-2.amazonaws.com/alpha/'+url_version+'/data/query'
        url = 'https://'+url_version+'.paxfinancial.ai/data/query'
        data = {}
        data['qtype'] = source_id
        data['__encoded_query'] = paxqueryengine.do_encode(query)
        return data




    def do_encode(request_obj):
        serial = pickle.dumps(request_obj)
        user_data_enc = base64.b64encode(serial).decode("ascii")                   
        return user_data_enc
    
    def do_decode(data_packet):
        #try:
        #    user_data_dev = base64.b64decode(data_packet)                   
        #except:
        from urllib.parse import unquote
        user_data_dev = base64.b64decode(unquote(data_packet))   
        data2 = pickle.loads(user_data_dev)
        return data2
    
    def do_encode_string(obj):
        string = json.dumps(obj,separators=(',', ':'))
        encoded = base64.b64encode(string.encode('ascii'))
        return encoded.decode('ascii') 

    def do_decode_string(data_packet):
        user_data_dev = base64.b64decode(data_packet)                   
        data2 = json.loads(user_data_dev.decode("ascii"))
        return data2
    
    def build_source(self,source_id,context_in=None,source_func=None,properties=None,errors=False,reload=True):
        global PaxFinancialAPIEndpointRegistry
        return  self.get_source(PaxFinancialAPIEndpointRegistry,source_id,context_in=context_in,source_func=source_func,properties=properties,errors=errors,reload=reload)
        

    def get_source(self,registry,source_id,context_in=None,source_func=None,properties=None,errors=False,reload=True):
        '''
        build the data source and store the required model data
        '''
        if source_id in self.source_map and not reload==True:
            return
        
        if source_id in registry and not reload==True:
            self.query_definitions[source_id] = registry[source_id]['query_definitions'] 
            self.query_objects[source_id] = registry[source_id]['query_objects'] 
            self.query_output_id[source_id] = registry[source_id]['query_output_id'] 
            self.query_input_id[source_id] = registry[source_id]['query_input_id'] 
            self.query_full_path[source_id] = registry[source_id]['query_full_path'] 
            return 
        #print("registered," + source_id)
        full_str = ""
        if not source_func is None:
            try:
                if type(source_func) == str:
                    full_str = source_func
                    lst = source_func.split('.')
                    module = '.'.join(lst[0:len(lst)-1])
                    func = lst[len(lst)-1]
                    source_func = localfindclass(func,module,context=globals(),reload=reload)
                    
            except Exception as e:
                #print("FAILED registered," + source_id + str(e))
                #if errors:
                raise(e)
                return [None,None,None,None] # Cant find the function
            self.source_map[source_id] = source_func
        [networkDef,out_id,input_id,context] = self.source_map[source_id](properties)
        auth_node = {'name':'authenticate',
                                     'type':'AuthorizeSection',
                                     'dependencies':{'input':{'api_key':['__ref','api_key'],
                                                              '__running_as_root':['__ref','__running_as_root'],
                                                              '__sigs':['__ref','__sigs'],
                                                              'query_func':source_id
                                                             }}    }    
        #if not 'authenticate' in networkDef or  networkDef ['authenticate'] == None:
        networkDef['authenticate'] = auth_node

        try:
            for key in networkDef.keys():
                if not key ==  'authenticate' and not networkDef[key]==None and not networkDef[key]['type'] == 'AuthorizeSection':
                    if not 'dependencies' in networkDef[key] or  networkDef[key]['dependencies']==None:
                        networkDef[key]['dependencies'] = {}
                    if not 'input' in networkDef[key]['dependencies'] or  networkDef[key]['dependencies']==None :
                        networkDef[key]['dependencies'] = {}
                    if type(networkDef[key]['dependencies']) == dict:
                        networkDef[key]['dependencies']['authenticate'] = ['__ref','authenticate']
        except Exception as e:
            import pprint 
            print('\n\n\n')
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!CANT AUTHENTICATE')
            pprint.pprint(networkDef[key])            
            raise(e)
        
        try:
            if context_in == None:
                context_in = {}
            context_class = globals()
            context_class.update(context)
            context_class.update(context_in)
            pn=ProcessingNetwork(networkDef,context=context_class)
            #print(">>>>>>>dsaving," + source_id )

            self.query_definitions[source_id] = networkDef 
            self.query_objects[source_id] = pn
            self.query_output_id[source_id] = out_id
            self.query_input_id[source_id] = input_id
            self.query_full_path[source_id] = full_str
            
            # Make an entry in the registry
            registry[source_id] = {}
            registry[source_id]['query_definitions'] =  self.query_definitions[source_id] 
            registry[source_id]['query_objects']  = self.query_objects[source_id] 
            registry[source_id]['query_output_id']  = self.query_output_id[source_id] 
            registry[source_id]['query_input_id']  = self.query_input_id[source_id] 
            registry[source_id]['query_full_path'] = self.query_full_path[source_id]
            registry[source_id]['source_map'] = self.source_map[source_id]
            
        except Exception as e:
            print("FAILED QUERY REGISTRATION!")
            import traceback
            traceback.print_exc()
            print("END -- FAILED QUERY REGISTRATION!")
            raise e
            
    def query_debug(self,filter_in,source_id):
        label = "query_debug"
        
        if '__encoded_query' in filter_in: # A direct encoding of a python object
            dic = paxqueryengine.do_decode(filter_in['__encoded_query'])
            filter_in.update(dic)

        if '__str_encoded_query' in filter_in: #An encoded json object
            try:
                encodedStr = filter_in['__str_encoded_query']
                decodedStr = urllib.parse.unquote(encodedStr)                
                dic = paxqueryengine.do_decode_string(decodedStr )
                filter_in.update(dic)
            except Exception as e:
                print('decode json string error:')
                print(filter_in['__str_encoded_query'])
                print(e)
                raise Exception("COULD NOT DECODE in PaxFinancialAPI " + str(filter_in))
                
        if self.query_input_id[source_id] == None:
            filter = filter_in
        else:
            filter = {self.query_input_id[source_id]:filter_in}

        out_id = self.query_output_id[source_id]
        try:
            res = self.query_objects[source_id].process(filter.copy(),rootIn=out_id)
        except Exception as  e:
            if "AuthorizeSection: Not Authorized!" in str(e):
                res = {self.query_output_id[source_id]:{"error":"User is not authorized."}}
            else:
                res = {self.query_output_id[source_id]:{"error":"Unknown error encountered."}}
            import traceback as tb
            res[self.query_output_id[source_id]]['traceback'] = tb.format_exc()
                
        return res
        
        
    def query(self,filter,source_id,remote=True,url_version='dev',  wait_seconds = 120,re_query_delay=5,show_url=False):
        time_start = datetime.datetime.utcnow()
        while (datetime.datetime.utcnow() - time_start).total_seconds() < wait_seconds:
            #print('query_wait',show_url)
            resp = self.query_wait(filter,source_id,remote,url_version,show_url)
            if type(resp) == dict and 'state' in resp and resp['state'] == 'updating':
                print(filter)
                print(resp)
                print('.',end='')
                time.sleep(re_query_delay)
                if 'force_refresh' in filter:
                    del(filter['force_refresh'])
            else:
                break
        return resp        
        
    def query_wait(self,filter,source_id,remote=True,url_version='dev',show_url=False):
        if '__encoded_query' in filter:
            #time_print_start(label+"_decode")
            dic = paxqueryengine.do_decode(filter['__encoded_query'])
            filter.update(dic)
            del(filter['__encoded_query'])
            #time_print_end(label+"_decode")
        #if remote == 'local':
        #    #time_print_start(label+"_local")
        #    loc = paxqueryengine.query_local(source_id,filter,url_version)
        #    #time_print_end(label+"_local")
        #    return loc
        
        if remote == 'ws':
            return paxqueryengine.query_websocket(source_id,filter,url_version)
        if remote  in [True,'http','https']:
            #print('query_remote',show_url)
            return paxqueryengine.query_remote(source_id,filter,url_version,show_url)
        #time_print_start(label+"_debug")
        if remote==False: 
            filter['__running_as_root'] = True
        return_dict =  self.query_debug(filter,source_id)
        #time_print_end(label+"_debug")
        if '__query_debug' in filter and filter['__query_debug'] == True:
            return return_dict
        #time_print_end(label)
        #time_list_print()
        
        return return_dict[self.query_output_id[source_id]]



class PaxFinancialAPIClass:
    def __init__(self,context_in=None,url_version='dev',api_key = None,reload=False):
        global PaxFinancialAPIEndpointRegistry
        self.api_key = api_key
        self.url_version = url_version
        #print(url_version)
        if context_in == None:
            context_in = globals()
        self.pq = paxqueryengine()
        self.current_attr = ""

        try: #" to load the registered queries if we are local. Otherwise fail out!"
            from  financialapi.rest.data.query import registeredQueries
            for q_key in registeredQueries:
                
                try: #" to load the registered queries if we are local. Otherwise fail out!"
                    q_dict = registeredQueries[q_key]
                    self.pq.build_source(q_key, context_in=context_in , source_func=q_dict['include_path']+'.'+q_dict['func'],reload=reload)
                    #print(">>>>>>>>>>loaded.. ", q_dict['func'] + ":"+q_dict['include_path'])
                except Exception as e:
                    import traceback
                    print("FAILED to load ", q_dict['func'] + ":")
                    traceback.print_exc()
                    raise e
                    pass
        except:
            pass
    def watch(self,q,remote=True,delay=1,offset=120):
        assert 'experiment_id' in q
        tsback = datetime.datetime.utcnow() - datetime.timedelta(seconds=offset)
        dat = self.get_output(q,remote=True)
        import time
        if 'api_key' not in q or q['api_key']==None:
            q['api_key'] = self.api_key        
        print('waiting.',end='')
        while dat == '':
            print('.',end='')
            ts = datetime.datetime.utcnow()+ datetime.timedelta(seconds=delay)
            q = { 'api_key' : q['api_key'],'experiment_id':q['experiment_id'],
                'start_date':tsback,'end_date':ts,}
            dat = self.get_output(q,remote=remote)
            time.sleep(delay)
        print(dat)
        while True:
            ts = datetime.datetime.utcnow()+ datetime.timedelta(seconds=5)
            q = { 'api_key' : q['api_key'],'experiment_id':q['experiment_id'],
                'start_date':tsback,'end_date':ts,}
            dat = self.get_output(q,remote=remote)
            tsback = datetime.datetime.utcnow() 
            print(dat)
            time.sleep(5)


    def __getattr__(self,attr):
        self.current_attr = attr
        return self.__run_query
    
    def __run_query(self,q,remote=True,wait_seconds = 120,re_query_delay=5,show_url=False):        
        if 'api_key' not in q or q['api_key']==None:
            q['api_key'] = self.api_key            
        return self.pq.query(q,self.current_attr,remote=remote,url_version=self.url_version,wait_seconds = wait_seconds,re_query_delay=re_query_delay,show_url=show_url)

## Wrapping a singleton around the PaxFinancial API in a manner that edits almost no code on the user side, or the class side (to reduce bugs)
class PaxFinancialAPISingleton():
    instance = None
    def Instance(context_in = None, url_version='dev',api_key = None,reload=True):
        try:
            inst = PaxFinancialAPISingleton.instance
            if PaxFinancialAPISingleton.instance == None:
                PaxFinancialAPISingleton.instance = PaxFinancialAPIClass(context_in=context_in,url_version=url_version,api_key = api_key,reload=reload)
            else:
                inst.api_key = api_key
                inst.url_version = url_version
                
                
        except:
            PaxFinancialAPISingleton.instance = PaxFinancialAPIClass(context_in=context_in,url_version=url_version,api_key = api_key,reload=reload)
        return PaxFinancialAPISingleton.instance

class PaxFinancialAPI(PaxFinancialAPIClass):
    pass
class Decelium(PaxFinancialAPIClass):
    #TODO -- move whole client connector into open source and revise PaxFinancial naming
    pass
class ImportedPaxFinancialAPI():
    instances = None
    
    def Instance(url_version,api_key=None,reload=False):
        if ImportedPaxFinancialAPI.instances == None:
            ImportedPaxFinancialAPI.instances = {}
        k = str(url_version)+str(api_key)
        if not url_version in ImportedPaxFinancialAPI.instances:
            ImportedPaxFinancialAPI.instances[k] = PaxFinancialAPISingleton.Instance(context_in = None,url_version=url_version,api_key = api_key,reload=reload)
            
        return ImportedPaxFinancialAPI.instances[k]
    
    
class SimpleCryptoRequester():
    '''
    A small class that can sit over top of Decelium Network connection, and sign each request as it is sent.
    Only use SimpleCryptoRequester if you ABSOLUTELY trust every local command you are running. If you run an odd program and 
    begin processing requests, they will all be auto-verified.
    
    The SimpleCryptoRequester is good for small local applications, and tasks like deploying websites, or doing admin work.

    Structure:    
    pq - a Decelium (or PaxFinancialAPIClass) instance, which has been connected
    users- {'test_admin':{'api_key': 'LONG_KEY', 
                        'private_key': 'SHORTER_KEY', 
                        'version': 'VERSION_INFO'}}    
    '''
    def __init__(self,pq,users):
        self.pq = pq
        self.users = users.copy()
        self.user_by_key = {}
        for user in self.users.values():
            self.user_by_key[user['api_key']] = user

    def __getattr__(self,attr):
        self.current_attr = attr
        return self.__run_secure_query
    
    def __run_secure_query(self,q,remote=False,wait_seconds = 120,re_query_delay=5,show_url=False):    
        if not 'api_key' in q:
            q['api_key'] = self.pq.api_key
        if not 'ses-' in q['api_key']:
            signers = [self.user_by_key[q['api_key']]]
            qsig = crypto.sign_request(q,signers)
        else:
            qsig = q
        func = getattr(self.pq, self.current_attr)
        return func(qsig,remote=remote,wait_seconds = wait_seconds,re_query_delay=re_query_delay,show_url=show_url)

from sys import getsizeof
from os.path import exists

class SimpleWallet(wallet):
    '''
    A simple wallet for holding decelium network artifacts. This wallet is a code level
    wallet only, and does not have a GUI for user interaction. Volunteers are presently working on
    hardware, javascript, and GUI wallet implementations! 

    Why? We had a lot of problems in web 3.0 with three issues:
    - sign transactions
    - store accounts and addresses
    - store generic secrets, keeping them encrypted too
    '''
    pass
    
    """
    def load(self,path=None,password=None,data=None):
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

    def save(self,path,password=None):
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

    def get_user(self,label):
        if not label in self.wallet:
            return {'error':'User is not in wallet manager'}
        return self.wallet[label]['user'] 

    def set_secret(self,label, sid, sjson):
        if not label in self.wallet:
            return {'error':'User is not in wallet manager'}
        try:
            a_string = crypto.do_encode_string(sjson)
        except:
            return {'error':'could not encode secret as json'}

        if getsizeof(a_string) > 1024*2:
            return {'error':'can not store a secret larger than 2kb'}

        self.wallet[label]['secrets'][sid] = sjson 
        return True
    
    def get_secret(self,label, sid):
        if not label in self.wallet:
            return {'error':'User is not registered'}
        if not sid in self.wallet[label]['secrets']:
            return {'error':'secret not saved'}
        return self.wallet[label]['secrets'][sid] 

    def list_secrets(self,label):
        if not label in self.wallet:
            return {'error':'User is not registered'}
        return list(self.wallet[label]['secrets'].keys()) 

    def get_raw(self):
        return self.wallet

    def recover_user(self,private_key):
        return crypto.generate_user_from_string(private_key,version='python-ecdsa-0.1')
    """
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
        print("unimplemented")
        #print(self.wallet);
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
                #print("astr",astr)
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
        #print("user",user)
        #print("label",label)
        #print("version",version)
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
        #print("account_data",account_data)
        if label == None:
            label = user['api_key']
        self.wallet[label] = account_data
        #user["some_data"] = "return"
        print("wallet",self.wallet)
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
        #print(wallet_dir)
        #print(os.getcwd())
        # look for a properly named .filename.dec.password
        password_file = wallet_dir / (wallet_path.stem + '.dec.password')
        #print(password_file)
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
