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
    def init(self):
        global state
        state['dw'] = Wallet.wallet()
        password = ""
        with open('/app/projects/.password','r') as f:
            password = f.read().strip()

        state['dw'].load(path="/app/projects/.wallet.dec", password=password)
        test_url = "https://dev.paxfinancial.ai/data/query"

        state['pq'] = network()
        state['pq'].connect({'type':'tcpip',
                             'url':test_url,
                             'port':5000,
                             'api_key':state['dw'].pubk("admin")})

        assert state['pq'].connected() 
        return True

    def register(self):
        global state
        port = 5003 + int(worker_id)
        q = state['pq'].gen_node_ping({
                   'name': "node-session-file-"+str(worker_id)+".node", 
                   'api_key':state['dw'].pubk("admin"),
                   'self_id':None,
                   'meta':{'test_id':"unit_test"},
                   'port':port})
        # print ("preping message")
        # print (q)


        # Any user can inspect the message here, to ensure they are comfortable with it
        qSigned = state['dw'].sign_request(q, ["admin"])
        resp = state['pq'].node_ping(qSigned)
        state['self_id'] = resp['self_id']        
        #print ("STARTING------------")
        #print (resp['self_id'])
        return True


    def listen(self):
        port = 5003 + int(worker_id)
        #api_key = state['dw'].pubk("admin")
        #new_id = None
        #name = "node-session-file-"+str(worker_id)+".node"
        #message = {'name': name, 
        #           'api_key':api_key,
        #           'self_id':state['self_id']
        #          }
        #qSigned = state['dw'].sign_request(message, ["admin"])
        #resp = state['pq'].register(qSigned)

        state['pq'].listen(port)
        assert state['pq'].listening()
        time.sleep(3)
        return True

    def shutdown(self):
        state['pq'].disconnect(0)
        return True

    def list_nodes(self):
        global state
        time.sleep(0.5)
        state['node_peers'] = []
        state['nodes'] = state['pq'].node_list()
        found = False
        for n in state['nodes']:            
            if n['self_id'] == state['self_id']:
                found = True
            else:
                if 'test_id' in n['connect_data']['meta']:
                    state['node_peers'].append(n)
                    print("passed inspection" + n['self_id'] )

        #print(state['node_peers'])
        return found

    def connect(self):
        global state
        state['sessions']=[]
        #print("CONNECTING")
        for peer_connect_data in state['node_peers']:
            connect_data = peer_connect_data
            connect_data['api_key'] = state['dw'].pubk("admin")
            sid = state['pq'].connect(connect_data)

            val = str(uuid.uuid4())
            respset = state['pq'].set_value({'api_key':connect_data['api_key'] ,
                                  'key':"test"+str(worker_id),
                                   'val':val},session_id=sid)


            #print("SETTING RESPONSE")
            #print(respset)
        time.sleep(2)
        return True

    def list_sessions(self):
        global state
        return True

    def store_variable(self):
        return True

    def force_disconnect(self):
        global state
        return True

    def get_disconnect_requests(self):
        global state
        return True

    def reconnect(self):
        global state
        return True

    def retrieve_variable(self):
        global state
        return True

    def purge_network_data(self):
        global state
        return True
    
def run_all_tests():
    print(1)
    c = core()
    print(2)
    steps = [
        c.init,
        c.register,
        c.listen,
        c.list_nodes,
        c.connect,
        #c.list_sessions,
        #store_variable,
        #force_disconnect,
        #get_disconnect_requests,
        #reconnect,
        #retrieve_variable,
        c.shutdown,
        #purge_network_data
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

            results.append(result)
            if result == False:
                break
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
        
    with open(f"worker{worker_id}_output.txt", "w") as f:
        for result in results:
            f.write(f"{result}\n")

if __name__ == "__main__":
    print("running "+str(sys.argv[1]))
    worker_id = int(sys.argv[1])
    state={}
    run_all_tests()
