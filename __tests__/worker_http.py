import sys
import time,datetime
sys.path.append("../")
import decelium_wallet.wallet as Wallet
from decelium_wallet.network import network
    
def init():
    global state
    state['dw'] = Wallet.wallet()
    password = ""
    with open('/app/projects/.password','r') as f:
        password = f.read().strip()

    state['dw'].load(path="/app/projects/wallet.dec", password=password)
    test_url = "https://dev.paxfinancial.ai/data/query"

    state['pq'] = network()
    state['pq'].connect({'type':'tcpip',
                         'url':test_url,
                         'port':5000,
                         'api_key':state['dw'].pubk("admin")})

    assert state['pq'].connected() 
    return True
    
def register():
    global state
    port = 5003 + int(worker_id)
    q = state['pq'].gen_node_ping({
               'name': "node-session-file-"+str(worker_id)+".node", 
               'api_key':state['dw'].pubk("admin"),
               'self_id':None,
               'port':port})
    print ("preping message")
    print (q)


    # Any user can inspect the message here, to ensure they are comfortable with it
    qSigned = state['dw'].sign_request(q, ["admin"])
    resp = state['pq'].node_ping(qSigned)
    state['self_id'] = resp['self_id']        
    print ("STARTING------------")
    print (resp['self_id'])
    return True
    

def listen():
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
    
def shutdown():
    state['pq'].disconnect(0)
    return True

def list_nodes():
    global state
    time.sleep(0.5)
    state['node_peers'] = []
    state['nodes'] = state['pq'].node_list()
    found = False
    for n in state['nodes']:            
        if n['self_id'] == state['self_id']:
            found = True
        else:
            state['node_peers'].append(n['self_id'] )
    print(state['node_peers'])

    return found
            
def connect():
    global state
    state['sessions']=[]
    for self_id in state['node_peers']:
        nd = state['pq'].node_pong({'self_id':self_id})
        if 'localhost' in nd['connect_data']['id']:
            print("found")
            print(nd)
        else:
            print(nd['connect_data']['id'])
        #state['sessions'].append(state['pq'].connect(node))
    return True
    
def list_sessions():
    global state
    return True
    
def store_variable():
    return True
    
def force_disconnect():
    global state
    return True
    
def get_disconnect_requests():
    global state
    return True
    
def reconnect():
    global state
    return True
    
def retrieve_variable():
    global state
    return True
    
def purge_network_data():
    global state
    return True
    
def run_all_tests():
    steps = [
        init,
        register,
        listen,
        list_nodes,
        connect,
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

    with open(f"worker{worker_id}_output.txt", "w") as f:
        for result in results:
            f.write(f"{result}\n")

if __name__ == "__main__":
    worker_id = int(sys.argv[1])
    state={}
    run_all_tests()
