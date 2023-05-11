import sys
import time,datetime
import os
try:
    from .wallet import wallet 
    from .network import network
    from .service import service
except:
    from decelium_wallet.wallet import wallet 
    from decelium_wallet.network import network
    from decelium_wallet.service import service

import uuid
import io

class core:
    
    #def load_wallet_from_disk(self):
    #    # TODO - Add in loading OP
    #    
    #    for root in ['./','../','../../','../../../','../../../../']:
    #        try:
    #            #print(root)
    #            self.dw = wallet()
    #            password = ""
    #            with open(root+'.password','r') as f:
    #                password = f.read().strip()
    #            with open(root+'.wallet.dec','r') as f:
    #                walletstr = f.read().strip()
    #            self.dw.load(path=root+'.wallet.dec', password=password)
    #            return True
    #        except:
    #            #import traceback as tb
    #            #tb.print_exc()
    #            pass
    #    return {"error":"could not find .password and .wallet.dec in parent path"}
    
    def load_wallet(self,data,password):
        assert type(data) == str
        assert type(password) == str
        self.dw = wallet()
        
        success = self.dw.load(data=data, password=password)
        return success
        #return {"error":"could not find .password and .wallet.dec in parent path"}
    
    def __init__(self):
        self.net = network()
        self.service = service()
        self.node_peer_list = None
    
    def gen_node_ping(self,port,name):
        c = self
        services = self.service.get_registry('public')
        q = c.net.gen_node_ping({
                   'name': name, 
                   'api_key':self.dw.pubk("admin"),
                   'self_id':None,
                   'services':services,
                   'meta':{'test_id':"unit_test"},
                   'port':port})
        return q
    
    def listen(self,port,name,public_handlers = []):
        
        for cfg in public_handlers:
            self.service.set_handler({"id":cfg[0],
                                           "name":cfg[0],
                               "handler":cfg[1],
                               "group":"public",
                               "runtime":None,
                               "meta":{}
                              })         
        
        
        q = self.gen_node_ping(port,name)
        qSigned = self.dw.sign_request(q, ["admin"])
        if "error" in qSigned:
            return qSigned
        resp = self.net.node_ping(qSigned)
        if "error" in resp:
            return resp
        self.self_id = resp['self_id']
        resp['api_key']=self.dw.pubk("admin")
        self.net.listen(resp,self.handle_connection) # Begin listening with the requested configuration!
        
        if not self.net.listening():
            return {"error":"could not start listening"}
        time.sleep(3)
        return True
    
    def sync_node_list(self):
        # TODO, choose who to sync with
        self.node_peer_list = []
        self.nodes = self.net.node_list() # Where are we pulling this list from?
        #import pprint
        #pprint.pprint(self.nodes)
        
        found = False
        for n in self.nodes:            
            if n['self_id'] == self.self_id:
                found = True
            else:
                if 'test_id' in n['connect_data']['meta']:
                    self.node_peer_list.append(n)
                    print("passed inspection" + n['self_id'] )
    def node_list(self):
        if self.node_peer_list == None:
            self.sync_node_list()
        return self.nodes
    
    def node_peers(self):
        if self.node_peer_list == None:
            self.sync_node_list()
        return self.node_peer_list
    
    def list_sessions(self):
        return self.list_sessions()
    
    def handle_connection(self,path,args):
        try:
            res = self.service.run(args)
        except:
            import traceback as tb
            res = tb.format_exc()
        return res 
    
    def initial_connect(self,target_url="https://dev.paxfinancial.ai/data/query",target_user="admin"):
        self.primary_session_id = self.net.connect({'type':'tcpip',
                             'url':target_url,
                             'port':5000,
                             'api_key':self.dw.pubk(target_user)},
                             self.handle_connection)

        assert self.net.connected() 
        return True   