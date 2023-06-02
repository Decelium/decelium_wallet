import sys
import time,datetime
sys.path.append("../")
from decelium_wallet.core import core
import uuid
import io
import json
from pprint import pprint

class WorkerHTTP():
    def __init__(self,core,node,peers):
        self.core = core
        self.node_address = node
        self.peer_ids = peers
    #############################
    ###
    ###  1. Load the wallet, and connect to the Miner
    ###
    # TODO -- split HTTP host from HTTP client, because you likely have one server for many clients. It makes no sense to instance many handlers with each connection. 
    '''
    for root in ['./','../','../../','../../../','../../../../']:
        try:
            with open(root+'.password','r') as f:
                password = f.read().strip()
            with open(root+'.wallet.dec','r') as f:
                walletstr = f.read().strip()
            return {"password":password,
                    "data":walletstr}
        except:
            #import traceback as tb
            #tb.print_exc()
            pass
    '''    
    def load_wallet_strings_from_disk(self):
        ret = {}
        wallets = self.core.discover_wallet()
        #look for a wallet named "test wallet" and load its contents
        for wal in wallets:
            if 'test_wallet' in wal['wallet']:
                with open(wal['wallet'],'r') as f:
                    ret['data'] = f.read()
                    assert len(ret['data']) > 0
                with open(wal['passfile'],'r') as f:
                    ret['password'] = f.read()
                    assert len(ret['password']) > 0
                return ret
                
        return {"error":"could not find .password and .wallet.dec in parent path"}
    
    def stage_init(self):
        raw_wallet = self.load_wallet_strings_from_disk()
        #print(raw_wallet)
        success = self.core.load_wallet(data=raw_wallet['data'],
                                        password=raw_wallet['password'])
        print("success",success)
        assert success == True
        # The initial connection is to a miner and relay. Through this system, a user can download addresses of even more public access points.
        assert self.core.initial_connect(target_url="https://"+self.node_address+"/data/query",
                          target_user="test_user") == True
        return True
    
    #############################
    ###
    ###  2. Broadcast that you are ready for connections
    ###
    def stage_broadcast(self):
        # TODO -- when to call core, and when to call core.net
        from MiniGetterSetter import MiniGetterSetter
        mimi = MiniGetterSetter()
        def do_echo(args,settings):
            return args

        port = 5003 + int(worker_id)
        name = "node-session-file-"+str(worker_id)+".node"
        public_handlers =  [("set_value",mimi.set_value),
                    ("get_value",mimi.get_value),
                    ("get_all",mimi.get_all),
                    ("do_echo",do_echo)]
        
        
        resp = self.core.listen(port,name,"test_user",public_handlers)
        if resp not in [True, False, None] and "error" in resp:
            return resp
        time.sleep(10)
        print("sleeping")
        return resp

    #############################
    ###
    ###  3. List all remote nodes. Ensure you can connect
    ###
    def stage_list_nodes(self):
        time.sleep(0.5)
        nodes = self.core.node_list()
        found = False
        count = 0
        for n in nodes:            
            if n['self_id'] == self.core.self_id:
                print ("found self")
                found = True
            else:
                if 'test_id' in n['connect_data']['meta']:
                    count = count + 1
                    print("py passed inspection" + n['self_id'] )
        try:
            assert len(self.peer_ids) == count
        except Exception as e:
            print("self.peer_ids",len(self.peer_ids))
            print("count",count)
            pprint(nodes)
            raise e
        return found

    #############################
    ###
    ###  4. Connect to every remote peer in a P2P manner. For each, set a value
    ###  
    def stage_set(self):
        self.sessions=[]
        for peer_connect_data in self.core.node_peers():
            connect_data = peer_connect_data
            connect_data['api_key'] = self.core.dw.pubk("test_user")
            sid = self.core.net.connect(connect_data,self.core.handle_connection)

            val = str(uuid.uuid4())
            respset = self.core.net.set_value({'api_key':self.core.dw.pubk("test_user") ,
                                  'key':"test"+str(worker_id),
                                   'val':val},session_id=sid)
            respget = self.core.net.get_value({'api_key':self.core.dw.pubk("test_user") ,
                                  'key':"test"+str(worker_id),},session_id=sid)
            
            print('respset',respset)
            print('respget',respget)
            
            assert respset == True
            assert respget == val
        time.sleep(2)
        return True


    #############################
    ###
    ###  4. Verify that we have all the data, locally
    ###
    def stage_verify(self):
        self.sessions=[]
        print("Stored the following data")
        vals = self.core.service.get_all({})
        import pprint
        pprint.pprint(vals)
        #for sid in self.core.list_sessions():
        #    print("for session")
        #
        #    val = str(uuid.uuid4())
        #    respset = self.core.net.set_value({'api_key':self.core.dw.pubk("admin") ,
        #                          'key':"test"+str(worker_id),
        #                           'val':val},session_id=sid)
        #    respget = self.core.net.get_value({'api_key':self.core.dw.pubk("admin") ,
        #                          'key':"test"+str(worker_id),},session_id=sid)
        
        return True
    
    
    
    def stage_shutdown(self):
        self.core.net.disconnect()
        return True
    
    
def run_all_tests(worker_id,node,peers):
    
    worker = WorkerHTTP(core(),node,peers)
    
    steps = [
        worker.stage_init,
        worker.stage_broadcast,
        worker.stage_list_nodes,
        worker.stage_set,
        worker.stage_verify,
        worker.stage_shutdown,
    ]

    results = []
    for i, step in enumerate(steps):
        print(step)
        print("----------------------------------------------------------")
        print(f"[{i}] Worker {worker_id}: {step.__name__}")
        result = False
        try:
            result = step()
        except Exception as e:
            import traceback as tb
            result = tb.format_exc()
            try:
                print("forcing shutdown . . .", end="")
                worker.stage_shutdown()
                print(" done")
            except:
                pass
        print(f"worker_http.py_{worker_id}: Step {step.__name__} {'succeeded' if result else 'failed'}")
        if not result == True:
            raise Exception(f"[{i}] Worker {worker_id}: {step.__name__}"+str(result))
        if result != True:
            break

if __name__ == "__main__":
    print("running "+str(sys.argv[1])+" on "+sys.argv[2])
    worker_id = int(sys.argv[1])
    node = sys.argv[2]
    peers = json.loads(json.loads(sys.argv[3]))
    
    run_all_tests(worker_id,node,peers)
