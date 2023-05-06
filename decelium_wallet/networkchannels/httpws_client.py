import json
import os
from os.path import exists
import datetime
import pickle
import base64
from flask import Flask, request
#from threading import Thread
from multiprocessing import Process


class jsondateencode_local:
    def loads(dic):
        return json.loads(dic,object_hook=jsondateencode_local.datetime_parser)
    def dumps(dic):
        return json.dumps(dic,default=jsondateencode_local.datedefault)

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

class httpws_client():
    def __init__(self,url_version=None,api_key=None,port=None, handle=None):
        self.url_version = url_version
        self.api_key = api_key
        print("httpws_client")
        print(url_version)
        print(port)
        
        #####
        self.port = port
        self.handle = handle
        self.app = Flask(__name__)
        self.shutdown_token = 'yyhhcthdjasif7'
        self.server_process = None
        
        
        @self.app.route('/', methods=['GET', 'POST'])
        @self.app.route('/<path:path>', methods=['GET', 'POST'])
        def index(path='/'):
            args = request.args if request.method == 'GET' else request.form
            return self.handle(path, args)

        @self.app.route('/disconnect', methods=['GET'])
        def disconnect():
            if self.shutdown_token is None:
                return 'Shutdown endpoint is not secured'
            if request.args.get('token') != self.shutdown_token:
                return 'Unauthorized', 401
            #self.app.stop()
            raise Exception ("Time for me to die")
            
            return 'Server shutting down...'
        
        self.server = None        
        
    def __getattr__(self,attr):
        self.current_attr = attr
        return self.__run_query

    def __run_query(self,q,remote=True,wait_seconds = 120,re_query_delay=5,show_url=False):        
        if 'api_key' not in q or q['api_key']==None:
            q['api_key'] = self.api_key            
        return self.query(q,self.current_attr,remote=remote,url_version=self.url_version,wait_seconds = wait_seconds,re_query_delay=re_query_delay,show_url=show_url)
    
    
    def query_websocket(self,source_id,query,url_version='dev'):
        from websocket import create_connection
        try:
            self.ws
        except:
            self.ws = {}
        if host not in self.ws:
            self.ws[host] = create_connection("ws://"+host+'/data/query')
        args = {}
        args['qtype'] = source_id
        args['__encoded_query'] = self.do_encode(query)
        args['host'] = host.split(':')[0]
        #args['url'] = '/data/query'
        try:
            self.ws[host].send(json.dumps(args))
            result =  self.ws[host].recv()
        except:
            self.ws[host].close()
            self.ws[host] = create_connection("ws://"+host+'/data/query')
            self.ws[host].send(json.dumps(args))
            result =  self.ws[host].recv()
            result = r'{}'.format(result)
            
        try:
            try:
                dat = jsondateencode_local.loads(result)
                if type(dat) == str:
                    dat = jsondateencode_local.loads(dat)
            except Exception as e:
                print(e)
                pass
            if type(dat) == str and dat[0] in ['[','{']:
                dat = jsondateencode_local.loads(dat)
        except Exception as e :
            print("DECODE ERROR")
            print(e)
            dat = r.text        
        return dat
    
    def query_remote(self,source_id,query,url_version='dev',show_url=False):
        import requests
        if show_url:
            print(url)
            print(query)
        data = {}
        data['qtype'] = source_id
        data['__encoded_query'] = self.do_encode(query)
        
        print("attempt",url_version)
        r = requests.post(url_version, data = data)        
        try:
            dat = jsondateencode_local.loads(r.text)
        except Exception as e :
            print(e)
            dat = r.text
        return dat
    
    def query_prepare(self,source_id,query,url_version='dev'):
        import requests
        data = {}
        data['qtype'] = source_id
        data['__encoded_query'] = self.do_encode(query)
        return data

    def do_encode(self,request_obj):
        serial = pickle.dumps(request_obj)
        user_data_enc = base64.b64encode(serial).decode("ascii")                   
        return user_data_enc
    
    def do_decode(self,data_packet):
        from urllib.parse import unquote
        user_data_dev = base64.b64decode(unquote(data_packet))   
        data2 = pickle.loads(user_data_dev)
        return data2
    
    def do_encode_string(self,obj):
        string = json.dumps(obj,separators=(',', ':'))
        encoded = base64.b64encode(string.encode('ascii'))
        return encoded.decode('ascii') 

    def do_decode_string(self,data_packet):
        user_data_dev = base64.b64decode(data_packet)                   
        data2 = json.loads(user_data_dev.decode("ascii"))
        return data2
    
        
    def query(self,filter,source_id,remote=False,url_version='dev',  wait_seconds = 120,re_query_delay=5,show_url=False):
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
        
    def query_wait(self,filter,source_id,remote=False,url_version='dev',show_url=False):
        if '__encoded_query' in filter:
            dic = self.do_decode(filter['__encoded_query'])
            filter.update(dic)
            del(filter['__encoded_query'])
        
        if remote == 'ws':
            return self.query_websocket(source_id,filter,url_version)
        if remote  in [True,'http','https']:
            return self.query_remote(source_id,filter,url_version,show_url)
        
        return None    


    def listen(self,port):
        #self.thread = Thread(target=self.app.run, kwargs={'port': self.port})
        #self.thread.start()        
        self.server_process = Process(target=self.app.run, kwargs={'port': port})
        self.server_process.start()        
        
        #self.server = self.app.run(port=self.port)
        return True

    def listening(self):
        return self.server_process is not None and self.server_process.is_alive()


    '''
    def disconnect(self):

        import requests
        if self.shutdown_token is None:
            return 'Shutdown endpoint is not secured'
        response = requests.get(f'http://localhost:{self.port}/disconnect?token={self.shutdown_token}')
        if response.status_code == 401:
            return 'Unauthorized'
        return response.text
    '''
    def disconnect(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.join()    