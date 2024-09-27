import sys
import time,datetime
import os
import subprocess
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
from threading import Timer


class core:

    def uuid_gen(seed_string= None):
        if seed_string != None:
            sha256_hash = hashlib.sha256(seed_string.encode()).hexdigest()
            uuid_like = f"{sha256_hash[:8]}-{sha256_hash[8:12]}-{sha256_hash[12:16]}-{sha256_hash[16:20]}-{sha256_hash[20:32]}"    
            return "obj-"+uuid_like
        else:
            return "obj-"+str(uuid.uuid4())
    
    def has_entity_prefix(self,string:str):
        assert type(string) == str,"objectid Must be a string " + str(string)
        valid_prefix = ['obj-','dir-','system_root']
        for prefix in valid_prefix:
            if string.startswith(prefix):
                return True
        return False
    def discover_wallet(self,root="./",password=None):
        res = wallet.discover(root,password)
        return res
    
    def __monitor_local_job_progress(self,proc,label):
        while True:
            output = proc.stdout.readline()
            if output:
                print(output.strip())
                sys.stdout.flush()  # Flush after each print            
            if output == '' and proc.poll() is not None:
                break
        res = proc.communicate()
        return  res[0],res[1]  

    def run_local_job(self,script,command,cwd):
        '''
        TODO - Merge / use nodejobs locally (?)
        '''
        #result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=cwd)
        print(command)
        with subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=cwd, text=True) as proc:
            return self.__monitor_local_job_progress(proc,script) 
        return None,None


    def run_remote_job(self,script,command,cwd):
        decw = self
        s = decw.dw.sign_request
        run_result = decw.net.node_job_run(decw.dw.sr({'api_key':decw.dw.pubk("admin"),
                                                       'job_id':script,
                                                       'job_name':script,
                                                       'command':command,
                                                       'cwd':cwd,
                                                       },["admin"]))
        list_data = decw.net.node_job_list(s({'api_key':decw.dw.pubk("admin"),'filter':{'self_id':script}},["admin"]))
        if 'error' in list_data:
            print(list_data)
        while (list_data[script]['status'] in ['starting','running']):
            time.sleep(3)
            print(".",end='')
            list_data = decw.net.node_job_list(s({'api_key':decw.dw.pubk("admin"),'filter':{'self_id':script}},["admin"]))
        job_logs = decw.net.node_job_logs(decw.dw.sr({'api_key':decw.dw.pubk("admin"),
                                                       'job_id':script,
                                                       },["admin"]))
        
        return job_logs[0],job_logs[1]

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
    @staticmethod
    def rd_path(path:str):
        with open(path,'r') as f:
            data = f.read()
        return data
    def load_wallet(self,data,password,mode='js'):
        assert type(data) == str
        assert type(password) == str
        self.dw = wallet()      
        success = self.dw.load(data=data, password=password,mode=mode)
        return success
    
    def __init__(self):
        self.target_user = 'admin'
        self.dw = wallet()          
        self.net = network()
        self.service = service()
        self.node_peer_list = None
    
    def gen_node_ping(self,port,name,wallet_user):
        c = self
        services = self.service.get_registry('public')
        if 'error' in services:
            services = {}
        q = c.net.gen_node_ping({
                   'name': name, 
                   'api_key':self.dw.pubk(wallet_user),
                   'self_id':None,
                   'services':services,
                   'meta':{'test_id':"unit_test"},
                   'port':port})
        return q
    
    ''' 
    def listen(self,port,name,wallet_user="admin",public_handlers = []):
        resp = self.do_ping(self,port,name,wallet_user,public_handlers)
        if "error" in resp:
            return resp
        
        self.self_id = resp['self_id']
        resp['api_key']=self.dw.pubk(wallet_user)
        self.net.listen(resp,self.handle_connection) # Begin listening with the requested configuration!
        
        if not self.net.listening():
            return {"error":"could not start listening"}
        time.sleep(3)
        
        
        def runPingsDef(nextFunc):
            t = Timer(ms / 1000., fn, args=args, kwargs=kwargs) 
            t.start() 
            resp = self.do_ping(self,port,name,wallet_user,public_handlers)
            return t
        
        return True
    '''    
    
    
    
    def do_ping(self,port,name,wallet_user="admin",public_handlers = []):
        for cfg in public_handlers:
            self.service.set_handler({"id":cfg[0],
                                           "name":cfg[0],
                               "handler":cfg[1],
                               "group":"public",
                               "runtime":None,
                               "meta":{}
                              })         
        
        
        q = self.gen_node_ping(port,name,wallet_user)
        qSigned = self.dw.sign_request(q, [wallet_user])
        if "error" in qSigned:
            return qSigned
        resp = self.net.node_ping(qSigned)
        if "error" in resp:
            resp["error"] = resp["error"] + " with message "+str(qSigned)
            return resp
        try:
            self.self_id = resp['self_id']
            return resp
        except:
            return {"error":"gen_node_ping response is invalid: "+ str(resp)}
        
        
    def complete_node_ping(self, port, name, wallet_user="admin"):
        # Generate node ping message
        node_ping_msg = self.gen_node_ping(port, name, wallet_user)

        print("-----node_ping_msg-----",node_ping_msg)

        # Sign the node ping message
        signed_msg = self.dw.sign_request(node_ping_msg , [wallet_user])
        if "error" in signed_msg:
            return signed_msg
        
        # Send the signed node ping message to the network
        resp = self.net.node_ping(signed_msg)
        
        if "error" in resp:
            resp["error"] += " with message "+str(signed_msg)
            
        return resp

    def set_interval(self, func, keep_running, sec, *args, **kwargs):
        def func_wrapper():
            if keep_running():
                self.set_interval(func, keep_running, sec, *args, **kwargs)
                func(*args, **kwargs)
            else:
                print("ENDING TIMER FOR "+str(func))
        t = Timer(sec, func_wrapper)
        t.start()
        return t    
    
    def listen(self,port,name,wallet_user="admin",public_handlers = []):
        resp = self.do_ping(port,name,wallet_user,public_handlers)
        if "error" in resp:
            return resp
        self.self_id = resp['self_id']
        resp['api_key']=self.dw.pubk(wallet_user)
        self.net.listen(resp,self.handle_connection) # Begin listening with the requested configuration!

        if not self.net.listening():
            return {"error":"could not start listening"}

        def run_pings_def():
            #if self.net.listening():
            #print("DOING PING")
            res = self.do_ping(port,name,wallet_user,public_handlers)
            #print(res)
        self.set_interval(run_pings_def,self.net.listening, 5)  # ping every 60 seconds

        return True
    
    def sync_node_list(self):
        # TODO, choose who to sync with
        self.node_peer_list = []
        self.nodes = self.net.node_list() # Where are we pulling this list from?
        #import pprint
        #pprint.pprint(self.nodes)
        print("------self.nodes----", self.nodes)
        found = False
        for n in self.nodes:            
            if n['self_id'] == self.self_id:
                found = True
            else:
                if 'test_id' in n['connect_data']['meta']:
                    self.node_peer_list.append(n)
                    print("passed inspection" + n['self_id'] )

    # TODO : This code is a temporary solution and may need to be revised
    def set_self_id(self, resp):
        self.self_id = resp['self_id'] 
                             
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
    '''
      async initial_connect(
    target_url = undefined,
    target_user = undefined,
    api_key = undefined
  ) {
    if (target_user == undefined)
          target_user = await this.dw.list_accounts()[0];
    if (!this.net) this.net = new network();
    let set_api_key = api_key;
    if (!set_api_key && target_user && this.dw)
      set_api_key = this.dw.pubk(target_user);
    if (!set_api_key) throw new Error("No valid credentials provided");    
    '''
    def initial_connect(self,target_url,target_user=None,api_key=None):
        if target_user == None:
            lst = self.dw.list_accounts()
            if len(lst) > 0:
                target_user = self.dw.list_accounts()[0]
        if self.net == None:
            self.net = network()
        set_api_key = api_key
        if set_api_key == None and target_user != None:
          set_api_key = self.dw.pubk(target_user)
        if set_api_key== None: 
            raise Exception("No valid credentials provided")
            
        self.primary_session_id = self.net.connect({'type':'tcpip',
                             'url':target_url,
                             'port':5000,
                             'api_key':set_api_key},
                             self.handle_connection)

        assert self.net.connected() 
        return True   