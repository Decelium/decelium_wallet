import sys
import time,datetime
sys.path.append("../")
import decelium_wallet.wallet as Wallet
from decelium_wallet.network import network
from decelium_wallet.service import service
import uuid
import io

'''
    
# Example usage:
if __name__ == "__main__":
    from service import service
    from MiniGetterSetter import MiniGetterSetter
    query = service.service()    
    
    mimi = MiniGetterSetter()
    
    def do_echo(args,settings):
        return args
    
    for cfg in [("set_value",mimi.set_value),
                ("get_value",mimi.get_value),
                ("do_echo",do_echo),
               
               ]:
        query.set_handler({"id":cfg[0],
                           "handler":cfg[1],
                           "group":"public",
                           "runtime":None,
                           "meta":{}
                          }) 
    
    
    # Usage #######
    req = {"key":"test_key","val":str(uuid.uuid4())}
    dec = query.set_value(req)
    print(dec)
    
    val = query.get_value({"key":"test_key"})  
    print(val)
    val = query.do_echo({"key":"test_key"})  
    print(val)
    
    import pprint
    pprint.pprint(query.get_registry('public'))
'''
class core:
    #############################
    ###
    ###     Core Methods
    ###
    ###
    #############################
    
    def load_wallet(self):
        # TODO - Add in loading OP
        
        for root in ['./','../','../../','../../../']:
            try:
                self.dw = Wallet.wallet()
                password = ""
                with open(root+'.password','r') as f:
                    password = f.read().strip()
                with open(root+'.wallet.dec','r') as f:
                    walletstr = f.read().strip()
                self.dw.load(path=root+'.wallet.dec', password=password)
                return True
            except:
                pass
        return {"error":"could not find .password and .wallet.dec in parent path"}
    
    def __init__(self):
        self.net = network()
        self.service = service()
        self.node_peer_list = None
    
    def gen_node_ping(self):
        c = self
        # TODO -- Look up registry
        # 
        # 
        services = self.service.get_registry('public')
        #print("FOUND SERVICES")
        #print(services)
        
        port = 5003 + int(worker_id)
        q = c.net.gen_node_ping({
                   'name': "node-session-file-"+str(worker_id)+".node", 
                   'api_key':self.dw.pubk("admin"),
                   'self_id':None,
                   'services':services,
                   'meta':{'test_id':"unit_test"},
                   'port':port})
        #print(q)
        #qSigned = c.dw.sign_request(q, ["admin"])
        #resp = c.net.node_ping(qSigned)
        #self.self_id = resp['self_id']  
        return q
    
    def start_broadcast(self):
        ### TODO - Figure out Signature interface
        port = 5003 + int(worker_id)
        #print(1)
        q = self.gen_node_ping()
        qSigned = self.dw.sign_request(q, ["admin"])
        #print(2)
        if "error" in qSigned:
            #print(2.25)
            #print(qSigned)
            return qSigned
        #print(2.5)
        resp = self.net.node_ping(qSigned)
        #print(3)
        if "error" in resp:
            return resp
        self.self_id = resp['self_id']        
        self.net.listen(port)
        ## TODO -- you should be selecting a session to listen on, and the port should be built in
        #print(4)
        if not self.net.listening():
            return {"error":"could not start listening"}
        time.sleep(3)
        #print(5)
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
    
    def handle_connection(self,path,args):
        try:
            res = self.service.run(args)
        except:
            import traceback as tb
            res = tb.format_exc()
        return res 
#############################
###
###     Stages Below
###
###
#############################

class WorkerHTTP():
    def __init__(self,core):
        self.core = core
        
    #############################
    ###
    ###  1. Load the wallet, and connect to the Miner
    ###
    # TODO -- split HTTP host from HTTP client, because you likely have one server for many clients. It makes no sense to instance many handlers with each connection. 

        
    
    def stage_init(self):
        success = self.core.load_wallet()
        assert success == True
        test_url = "https://dev.paxfinancial.ai/data/query"
        self.tst_sid = self.core.net.connect({'type':'tcpip',
                             'url':test_url,
                             'port':5000,
                             'api_key':self.core.dw.pubk("admin")},
                             self.core.handle_connection)

        assert self.core.net.connected() 
        return True
    
    #############################
    ###
    ###  2. Broadcast that you are ready for connections
    ###
    def stage_broadcast(self):
        # TODO -- Look up registry
        # TODO -- when to call core, and when to call core.net
        from MiniGetterSetter import MiniGetterSetter
        

        mimi = MiniGetterSetter()

        def do_echo(args,settings):
            return args

        for cfg in [("set_value",mimi.set_value),
                    ("get_value",mimi.get_value),
                    ("do_echo",do_echo),

                   ]:
            self.core.service.set_handler({"id":cfg[0],
                                           "name":cfg[0],
                               "handler":cfg[1],
                               "group":"public",
                               "runtime":None,
                               "meta":{}
                              }) 


        # Usage #######
        #req = {"key":"test_key","val":str(uuid.uuid4())}
        #dec = self.core.service.set_value(req)
        #print(dec)

        #val = self.core.service.get_value({"key":"test_key"})  
        #print(val)
        #val = self.core.service.do_echo({"key":"test_key"})  
        #print(val)
        
        resp = self.core.start_broadcast()
        return resp

    #############################
    ###
    ###  3. List all remote nodes. Ensure you can connect
    ###
    def stage_list_nodes(self):
        time.sleep(0.5)
        nodes = self.core.node_list()
        found = False
        
        for n in nodes:            
            if n['self_id'] == self.core.self_id:
                print ("found self")
                found = True
            else:
                if 'test_id' in n['connect_data']['meta']:
                    print("passed inspection" + n['self_id'] )

        return found

    #############################
    ###
    ###  4. Connect to every remote peer in a P2P manner. For each, set a value
    ###
    def stage_set(self):
        self.sessions=[]
        #print("CONNECTING")
        for peer_connect_data in self.core.node_peers():
            print("a")
            connect_data = peer_connect_data
            print("b")
            connect_data['api_key'] = self.core.dw.pubk("admin")
            print("c")
            sid = self.core.net.connect(connect_data,self.core.handle_connection)
            print("d")

            val = str(uuid.uuid4())
            print("e")
            respset = self.core.net.set_value({'api_key':self.core.dw.pubk("admin") ,
                                  'key':"test"+str(worker_id),
                                   'val':val},session_id=sid)

            print("f")

            #print("SETTING RESPONSE")
            #print(respset)
        time.sleep(2)
        return True


    def stage_shutdown(self):
        self.core.net.disconnect()
        return True
    
    def stage_list_sessions(self):
        return True

    def stage_store_variable(self):
        return True

    def stage_force_disconnect(self):
        return True

    def stage_get_disconnect_requests(self):
        return True

    def stage_reconnect(self):
        return True

    def stage_retrieve_variable(self):
        return True

    def stage_purge_network_data(self):
        return True
    
def run_all_tests():
    
    worker = WorkerHTTP(core())
    
    steps = [
        worker.stage_init,
        worker.stage_broadcast,
        worker.stage_list_nodes,
        worker.stage_set,
        #c.stage_list_sessions,
        #c.stage_store_variable,
        #c.stage_force_disconnect,
        #c.stage_get_disconnect_requests,
        #c.stage_reconnect,
        #c.stage_retrieve_variable,
        worker.stage_shutdown,
        #c.stage_purge_network_data
    ]

    results = []
    for i, step in enumerate(steps):
        print(step)
        
        output_buffer = io.StringIO()
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = output_buffer, output_buffer
        
        try:        
            print("--------------------------------------------------")
            print(f"[{i}] Worker {worker_id}: Running step {step.__name__}")
            result = False
            try:
                result = step()
            except Exception as e:
                import traceback as tb
                tb.print_exc()
                print(e)
            if not result == True:
                print(result)
            results.append(result)
            print(f"worker_http.py_{worker_id}: Step {step.__name__} {'succeeded' if result else 'failed'}")
            print("--------------------------------------------------")
        except:
            import traceback as tb
            tb.print_exc()
            # Restore the original stdout and stderr
            sys.stdout, sys.stderr = old_stdout, old_stderr
            
        finally:
            # Restore the original stdout and stderr
            sys.stdout, sys.stderr = old_stdout, old_stderr
            pass
        # Print the buffered output
        print(output_buffer.getvalue())
        output_buffer.close()
        if result != True:
            break
        
    with open(f"worker{worker_id}_output.txt", "w") as f:
        for result in results:
            f.write(f"{result}\n")

if __name__ == "__main__":
    print("running "+str(sys.argv[1]))
    worker_id = int(sys.argv[1])
    run_all_tests()
