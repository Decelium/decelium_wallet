from decelium_wallet.networkchannels.httpws_client import httpws_client
import datetime
import uuid

def load_pq(path,password,url_version,target_user):
    dw = decelium.SimpleWallet()
    dw.load(path,password)
    accts = dw.list_accounts()

    #print(accts)
    #print(target_user)
    #print(dw.get_user(target_user))

    assert target_user in accts
    user = dw.get_user(target_user)
    pq_raw = decelium.Decelium(url_version=url_version,api_key=user['api_key'])
    pq = decelium.SimpleCryptoRequester(pq_raw,{user['api_key']:user})
    return pq, user['api_key'], dw

class network:
    '''
            state['pq'].connect({'type':'tcpip',
                             'url':test_url,
                             'api_key':state['dw'].pubk("admin")})

    '''
    def __init__(self):
        #self.session1=httpws_client(self.test_url,self.api_key, 5000,self.handle)
        self.sessions = {}
        
    def __getattr__(self,attr):
        self.current_attr = attr
        return self.__run_query
    
    def __run_query(self, *args,session_id=None, **kwargs):
        session_id_selected = session_id
        if session_id_selected == None:
            session_id_selected = list(self.sessions.keys())[0] 
        inst = self.sessions[session_id_selected]['instance']
        method_to_call = getattr(inst, self.current_attr)
        if 'session_id' in kwargs: 
            del(kwargs['session_id'])
        return method_to_call(*args, **kwargs)
    
    def handle(args):
        print("in handle")
        
        return "yes"
    
    def gen_node_ping(self,args):
        for k in ['name','api_key','self_id','port']:
            if not k in args:
                return {"error":"network: you must provide "+k}
        message = {'name': args['name'], 
                   'api_key':args['api_key'],
                   'self_id':args['self_id'],

                   'connect_data':{"id":"http://localhost:"+str(args['port']),
                                    'services':{"id_download_data":{"id":"id_download_data",
                                                                    "name":"download_data",}},
                                     "type":"tcpip"}
                  }        
        return message
    
    
        
    #def node_ping(self, node_def):
    #    result=self.session1.node_ping(node_def,remote=True)
    #    return result
    
    def node_list(self,session_id=None):
        time_10_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=3)
        query = {
            "connect_data.ping": {"$gte": time_10_minutes_ago},
            "file_type":"node"
        }
        if session_id == None:
            session_id = list(self.sessions.keys())[0]
        self.nodes = self.sessions[session_id]['instance'].list({"attrib":query,'limit':10})
        return self.nodes         
        
    
    
    def list_nodes(self):
        node_list = []
        for i in range(5):
            node_list.append( {'name': 'node-session-file-'+str(i)+'.node', 
                   'api_key':self.api_key,
                   'self_id':str(i),

                  'connect_data':{"id":"node-session-test",
                                    'services':{"id_download_data":{"id":"id_download_data",
                                                                    "name":"download_data",}},
                                     "type":"tcpip"}
                  })
        
        return node_list;
    
    def connect(self,args):
        if type(args) == dict:
            assert 'type' in args and args['type']=='tcpip'
            assert 'url' in args and len(args['url']) > 4
            assert 'port' in args and type(args['port']) == int
            assert 'api_key' in args and len(args['api_key']) > 4
            inst_id = str(uuid.uuid4())
            self.sessions[inst_id]= args
            self.sessions[inst_id]['instance'] = httpws_client(args['url'],args['api_key'], args['port'],self.handle)
            return True
        else:
            return False
        return False
    
    def list_sessions(self):
        return []
    
    def store_variable(self,session_id,key,value):
        return True
    
    def get_variable(self,session_id,key):
        return True
    
    def disconnect(self,session_id):
        for skey in self.sessions:
            disconnect = self.sessions[skey]['instance'].disconnect()
        return True
    
    def delete_variable(self,session_id,key):
        return True
    
    def connected(self):
        return len(self.sessions) > 0
    
    
    def listening(self):
        return True
    