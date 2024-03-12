import json
import datetime
import pickle
import base64
import requests
import time
import ipfshttpclient
import os

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

class http_client():
    def __init__(self, url_version=None, api_key=None,port=None):
        self.url_version = url_version
        self.api_key = api_key
        self.port = port

    def __getattr__(self, attr):
        self.current_attr = attr
        return self.__run_query

    def __run_query(self, q, remote=True, wait_seconds=120, re_query_delay=5, show_url=False):        
        if 'api_key' not in q or q['api_key'] == None:
            q['api_key'] = self.api_key            
        return self.query(q, self.current_attr, remote=remote, url_version=self.url_version, 
                          wait_seconds=wait_seconds, re_query_delay=re_query_delay, show_url=show_url)

    def create_ipfs_connection(self,connection_settings):
        api = None
        if 'host' not in connection_settings:
            return  {"error": "ipfs host must be specified in connection_settings"},None
        if 'port' not in connection_settings:
            return {"error": "ipfs port must be specified in connection_settings"},None
        if 'protocol' not in connection_settings:
            return {"error": "ipfs protocol must be specified in connection_settings"},None

        # If 'headers' is not present, initialize it to an empty dictionary 
        if 'headers' not in connection_settings:
            connection_settings['headers'] = {}
            
        ipfs_string = "/dns/"+str(connection_settings["host"])+"/tcp/"+str(connection_settings["port"])+"/"+str(connection_settings["protocol"])
            
        if len(connection_settings['headers']) > 0:
            api = ipfshttpclient.connect(ipfs_string,headers=connection_settings['headers'])
        else:
            api = ipfshttpclient.connect(ipfs_string)
        return {"message":"success"}, api

    def apply_alternate_processing(self,filter,source_id):
        if source_id == "create_ipfs":
            return self.processing_create_ipfs(filter,source_id)
        if source_id == "remove_ipfs":
            return self.processing_remove_ipfs(filter,source_id)
        if source_id == "check_pin_status":
            return self.processing_check_pin_status(filter,source_id)
            
        else:
            return None
    def latest_remote_pin_list(self,connection_settings):
        do_refresh = False
        try:
            assert len(self.saved_pins) > 0
        except:
            do_refresh = True
        if do_refresh == True:
            message,api = self.create_ipfs_connection(connection_settings)
            pin_response = api.pin.ls(type='recursive')
            pins = []
            for pin in pin_response['Keys']:
                pins.append(pin)
            self.saved_pins = pins
            
        return self.saved_pins

    def processing_check_pin_status(self, filter,source_id):
        if 'connection_settings' not in filter:
            return {"error": "connection_settings argument required i.e. {host:str, port:int, protocol:str, headers:{authorization:str}}"}
        connection_settings = filter['connection_settings']

        if 'cid' not in filter:
            return {"error":"Need need a 'cid' argument"}
        cid = filter['cid']
        
        pins = self.latest_remote_pin_list(connection_settings)

        if cid in pins:
            return True
        return False

    def processing_create_ipfs(self,filter,source_id):

        if source_id == "create_ipfs" and 'file_type' in filter and filter['file_type'] == 'ipfs' and 'payload_type' in filter:
            # Check if 'connection_settings' is present in the 'filter' dictionary 
            if 'connection_settings' not in filter:
                return {"error": "connection_settings argument required i.e. {host:str, port:int, protocol:str, headers:{authorization:str}}"}
            connection_settings = filter['connection_settings']
            message,api = self.create_ipfs_connection(connection_settings)
            if 'error' in message.keys():
                return message

            if filter['payload_type'] == 'ipfs_pin_list':
                try:
                    # Create an empty directory on IPFS
                    res = api.object.new(template="unixfs-dir")
                    if os.path.isfile( filter['payload']):
                        with open(filter['payload'],'r') as f:
                            filter['payload'] = json.loads(f.read())
                    if 'Links' in filter['payload']:
                        filter['payload'] = filter['payload']['Links']
                    # Iterate over the payload to link each object to the newly created directory
                    for item in filter['payload']:
                        name = item['Name']
                        hash = item['Hash']
                        # Construct the path with the name for the item to be linked under the directory
                        path = f"{res}/{name}"
                        # Use object patch add-link to link the object to the directory
                        res = api.object.patch.add_link(res['Hash'], name, hash)
                        # res = res['Hash']
                        print(res.keys())
                    # After linking all items, the 'empty_dir_cid' will be the CID of the final directory
                    # return  [{'name': res['Name'], 'cid': res['Hash'], 'size': res['Size']}]

                    return  [{'name': '', 'cid': res['Hash'], 'size': None}]
                except Exception as e:
                    import traceback as tb
                    print(tb.format_exc())
                    return {"error": str(e) + tb.format_exc()}

            # Existing condition for 'local_path' payload type 
            elif filter['payload_type'] == 'local_path':
                #res = api.add(filter['payload'],recursive=True)
                original_directory = os.getcwd()
                try:
                    path = filter['payload']
                    if os.path.isdir(path):
                        # If the path is a directory, change the working directory and add recursively 
                        os.chdir(path)
                        res = api.add('.', recursive=True)
                    elif os.path.isfile(path):
                        # If the path is a file, add the file directly without changing the working directory
                        res = api.add(path)
                    else:
                        print("The provided path does not exist or is not a file/directory.")

                finally:
                    os.chdir(original_directory)            
            
                try:
                    dict_list = [{'name': res['Name'], 'cid': res['Hash'], 'size': res['Size']}]
                except:
                    dict_list = [{'name': item['Name'], 'cid': item['Hash'], 'size': item['Size']} for item in res]
                for pin in dict_list:
                    pin_resp = api.pin.add(pin['cid'])
                    #print(pin_resp)

                root = {}
                for item in dict_list:
                    if item['name'] == "":
                        item['root'] = True
                        break
                return dict_list
        return None

    # TODO Migrate updates to JS
    # TODO Migrate FROM js as well
    def processing_remove_ipfs(self,filter,source_id):

        if source_id == "remove_ipfs"  and 'payload_type' in filter and filter['payload_type'] ==  'cid':
            # Check if 'connection_settings' is present in the 'filter' dictionary 
            if 'connection_settings' not in filter:
                return {"error": "connection_settings argument required i.e. {host:str, port:int, protocol:str, headers:{authorization:str}}"}
            connection_settings = filter['connection_settings']
            message,api = self.create_ipfs_connection(connection_settings)
            if 'error' in message.keys():
                return message
            if type(filter['payload']) == str:
                lst = [filter['payload']]
            elif type(filter['payload']) == list: 
                lst = filter['payload']
            else:
                return {"error":"payload must be a CID or list of CIDs"}
            res = {}
            for cid in lst:
                try:
                    resp = api.pin.rm(cid)
                    if cid==resp['Pins'][0]:
                        res[cid]=  {"removed":True}
                    else:
                        res[cid]= {"removed":False,"message":str(resp)}
                except:
                    import traceback as tb
                    res[cid]= {"removed":False,"message":tb.format_exc()}
                    
            return res
        return None

    def query(self, filter, source_id, remote=False, url_version='dev',  wait_seconds = 120, re_query_delay=5, show_url=False):
        time_start = datetime.datetime.utcnow()
        filter_result = self.apply_alternate_processing(filter,source_id)
        if filter_result != None:
            return filter_result        
        
        while (datetime.datetime.utcnow() - time_start).total_seconds() < wait_seconds:
            resp = self.query_wait(filter, source_id, remote, url_version, show_url)
            if type(resp) == dict and 'state' in resp and resp['state'] == 'updating':
                print('.',end='')
                time.sleep(re_query_delay)
                if 'force_refresh' in filter:
                    del(filter['force_refresh'])
            else:
                break
        return resp   

    def query_wait(self, filter, source_id, remote=False, url_version='dev', show_url=False):
        if '__encoded_query' in filter:
            dic = self.do_decode(filter['__encoded_query'])
            filter.update(dic)
            del(filter['__encoded_query'])

        if remote in [True, 'http', 'https']:
            resp = self.query_remote(source_id, filter, url_version, show_url)
            return resp
        return {"error":"No query processed"}

    def query_remote(self, source_id, query, url_version='dev', show_url=False):
        data = {}
        data['qtype'] = source_id
        data['__encoded_query'] = self.do_encode(query)

        if show_url:
            print(url_version)
            print(query)

        r = requests.post(url_version, data=data)

        try:
            dat = jsondateencode_local.loads(r.text)
        except Exception as e:
            print(e)
            dat = r.text
        return dat

    def do_encode(self, request_obj):
        serial = pickle.dumps(request_obj)
        user_data_enc = base64.b64encode(serial).decode("ascii")                   
        return user_data_enc
    
    def do_decode(self, data_packet):
        from urllib.parse import unquote
        user_data_dev = base64.b64decode(unquote(data_packet))   
        data2 = pickle.loads(user_data_dev)
        return data2
    
    def do_encode_string(self, obj):
        string = json.dumps(obj, separators=(',', ':'))
        encoded = base64.b64encode(string.encode('ascii'))
        return encoded.decode('ascii') 

    def do_decode_string(self, data_packet):
        user_data_dev = base64.b64decode(data_packet)                   
        data2 = json.loads(user_data_dev.decode("ascii"))
        return data2
