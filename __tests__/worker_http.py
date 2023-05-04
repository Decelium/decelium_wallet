import sys
import time
sys.path.append("../")
import decelium_wallet.wallet as Wallet
from decelium_wallet.network import network

    # Test Manual Query
    # We load a wallet class, and manually sign a transaction.
    # This is more secure, as it can control signatures on a message by message basis.
    
def init():
    global state
    try:
        state['dw'] = Wallet.wallet()
        password = ""
        with open('/app/projects/.password','r') as f:
            password = f.read().strip()
            
        state['dw'].load(path="/app/projects/wallet.dec", password=password)
        
        test_url = "https://dev.paxfinancial.ai/data/query"

        state['pq'] = network(test_url,state['dw'].pubk("admin"))
        assert state['pq'].connected() 
        return True
    except Exception as e:
        import traceback as tb
        tb.print_exc()
        print(e)
        return False
    
def register():
    global state
    try:
        #'connect_data':{"id":"node-session-test",
        #                            'services':{"id_download_data":{"id":"id_download_data",
        #                                                            "name":"download_data",}},
        #                             "type":"tcpip"}
        
        api_key = state['dw'].pubk("admin")
        new_id = None
        name = "node-session-file-"+str(worker_id)+".node"
        message = {'name': name, 
                   'api_key':api_key,
                   'self_id':new_id,

                   'connect_data':{"id":"UNDEFINED",
                                    'services':{"id_download_data":{"id":"id_download_data",
                                                                    "name":"download_data",}},
                                     "type":"tcpip"}
                  }
        qSigned = state['dw'].sign_request(message, ["admin"])
        resp = state['pq'].register(qSigned)
        state['self_id'] = resp['self_id']
        
        #print("register result")
        #print(resp)
        #print(qSigned)
        
        
        
        print ("STARTING")
        
        return True
    
    
    except Exception as e:
        import traceback as tb
        tb.print_exc()
        print(e)
        return False

def listen():
    try:
        port = 5003 + int(worker_id)
        api_key = state['dw'].pubk("admin")
        new_id = None
        name = "node-session-file-"+str(worker_id)+".node"
        message = {'name': name, 
                   'api_key':api_key,
                   'self_id':state['self_id'],

                   'connect_data':{"id":"http://localhost:"+str(port),
                                    'services':{"id_download_data":{"id":"id_download_data",
                                                                    "name":"download_data",}},
                                     "type":"tcpip"}
                  }
        qSigned = state['dw'].sign_request(message, ["admin"])
        resp = state['pq'].register(qSigned)
        
        state['pq'].listen(port)
        assert state['pq'].listening()
        time.sleep(3)
        return True
    except:
        import traceback as tb
        tb.print_exc()
        print(e)
        return False
    
def shutdown():
    try:
        state['pq'].disconnect(1)
        return True
    except:
        import traceback as tb
        tb.print_exc()
        print(e)
        return False

    
    
def list_nodes():
    global state
    try:
        time.sleep(0.5)
        state['nodes'] = state['pq'].list_nodes()
        assert len(state['nodes'])==5
        return True
    except Exception as e:
        print(e)
        return False
    
def connect():
    global state
    try:
        state['sessions']=[]
        for node in state['nodes']:
            state['sessions'].append(state['pq'].connect(node))
        return True
    except Exception as e:
        print(e)
        return False
    
def list_sessions():
    global state
    try:
        # Insert session listing code here
        return True
    except Exception as e:
        print(e)
        return False
    
def store_variable():
    try:
        # Insert variable storing code here
        return True
    except Exception as e:
        print(e)
        return False
    
def force_disconnect():
    global state
    try:
        # Insert force disconnect code here
        return True
    except Exception as e:
        print(e)
        return False
    
def get_disconnect_requests():
    global state
    try:
        # Insert disconnect request retrieval code here
        return True
    except Exception as e:
        print(e)
        return False
    
def reconnect():
    global state
    try:
        # Insert reconnect code here
        return True
    except Exception as e:
        print(e)
        return False
    
def retrieve_variable():
    global state
    try:
        # Insert variable retrieval code here
        return True
    except Exception as e:
        print(e)
        return False
    
def purge_network_data():
    global state
    try:
        # Insert network data purging code here
        return True
    except Exception as e:
        print(e)
        return False
    
def run_all_tests():
    steps = [
        init,
        register,
        listen,
        #list_nodes,
        #connect,
        #list_sessions,
        #store_variable,
        #force_disconnect,
        #get_disconnect_requests,
        #reconnect,
        #retrieve_variable,
        shutdown,
        #purge_network_data
    ]

    results = []
    for i, step in enumerate(steps):
        #print(f"Worker {worker_id}: Running step {step.__name__}")
        result = step()
        results.append(result)
        if result == False:
            break
        print(f"worker_http.py_{worker_id}: Step {step.__name__} {'succeeded' if result else 'failed'}")

    with open(f"worker{worker_id}_output.txt", "w") as f:
        for result in results:
            f.write(f"{result}\n")

if __name__ == "__main__":
    worker_id = int(sys.argv[1])
    state={}
    run_all_tests()
