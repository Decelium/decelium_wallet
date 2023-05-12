import sys
import time,datetime
sys.path.append("../")
from decelium_wallet.core import core
import uuid
import io

class WorkerHTTP():
    def __init__(self,core):
        self.core = core
        
    #############################
    ###
    ###  1. Load the wallet, and connect to the Miner
    ###
    # TODO -- split HTTP host from HTTP client, because you likely have one server for many clients. It makes no sense to instance many handlers with each connection. 
    def load_wallet_strings_from_disk(self):
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
        return {"error":"could not find .password and .wallet.dec in parent path"}
    
    def stage_init(self):
        raw_wallet = self.load_wallet_strings_from_disk()
        #print(raw_wallet)
        success = self.core.load_wallet(data=raw_wallet['data'],
                                        password=raw_wallet['password'])
        print("success",success)
        assert success == True
        # The initial connection is to a miner and relay. Through this system, a user can download addresses of even more public access points.
        assert self.core.initial_connect(target_url="https://dev.paxfinancial.ai/data/query",
                          target_user="admin") == True
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
        
        
        resp = self.core.listen(port,name,public_handlers)
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
        
        for n in nodes:            
            if n['self_id'] == self.core.self_id:
                print ("found self")
                found = True
            else:
                if 'test_id' in n['connect_data']['meta']:
                    print("py passed inspection" + n['self_id'] )

        return found

    #############################
    ###
    ###  4. Connect to every remote peer in a P2P manner. For each, set a value
    ###
    def stage_set(self):
        self.sessions=[]
        for peer_connect_data in self.core.node_peers():
            connect_data = peer_connect_data
            connect_data['api_key'] = self.core.dw.pubk("admin")
            sid = self.core.net.connect(connect_data,self.core.handle_connection)

            val = str(uuid.uuid4())
            respset = self.core.net.set_value({'api_key':self.core.dw.pubk("admin") ,
                                  'key':"test"+str(worker_id),
                                   'val':val},session_id=sid)
            respget = self.core.net.get_value({'api_key':self.core.dw.pubk("admin") ,
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
    
    
def run_all_tests():
    
    worker = WorkerHTTP(core())
    
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
        
        output_buffer = io.StringIO()
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = output_buffer, output_buffer
        
        try:        
            print("----------------------------------------------------------")
            print(f"[{i}] Worker {worker_id}: {step.__name__}")
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
    
    #worker.stage_shutdown()
    with open(f"worker{worker_id}_output.txt", "w") as f:
        for result in results:
            f.write(f"{result}\n")

if __name__ == "__main__":
    print("running "+str(sys.argv[1]))
    worker_id = int(sys.argv[1])
    run_all_tests()
