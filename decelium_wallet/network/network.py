from decelium_wallet.network.httpws_client import httpws_client

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

class Network:
    
    def __init__(self, test_url, api_key):
        self.test_url = test_url
        self.api_key = api_key
        self.session1=httpws_client(self.test_url,self.api_key)
        
    
    def register(self, node_def):
        result=self.session1.node_ping(node_def,remote=True)
        print(result)
        return True
    
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
    
    def connect(self,node_id):
        return True
    
    def list_sessions(self):
        return []
    
    def store_variable(self,session_id,key,value):
        return True
    
    def get_variable(self,session_id,key):
        return True
    
    def disconnect(self,session_id):
        return True
    
    def delete_variable(self,session_id,key):
        return True
    
    def connected(self):
        return True
    
    def listen(self):
        return True
    
    def listening(self):
        return True
    