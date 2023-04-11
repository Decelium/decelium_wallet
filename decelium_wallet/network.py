import json
import os
from os.path import exists


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

class query():
    def __init__(self):
        pass
    
    def run_websocket(source_id,query,url_version='dev'):
        from websocket import create_connection
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
    
    def run_remote(source_id,query,url_version='dev',show_url=False):
        import requests
        if show_url:
            print(url)
            print(query)
        data = {}
        data['qtype'] = source_id
        data['__encoded_query'] = paxqueryengine.do_encode(query)
        r = requests.post(url, data = data)        
        try:
            dat = jsondateencode_local.loads(r.text)
        except Exception as e :
            print(e)
            dat = r.text
        return dat
    
    def run_prepare(source_id,query,url_version='dev'):
        import requests
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
            dic = paxqueryengine.do_decode(filter['__encoded_query'])
            filter.update(dic)
            del(filter['__encoded_query'])
        
        if remote == 'ws':
            return paxqueryengine.query_websocket(source_id,filter,url_version)
        if remote  in [True,'http','https']:
            return paxqueryengine.query_remote(source_id,filter,url_version,show_url)
        
        return None    