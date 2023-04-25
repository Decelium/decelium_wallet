import sys
import time

import decelium_wallet.wallet as Wallet
from decelium_wallet.network.network import Network

    # Test Manual Query
    # We load a wallet class, and manually sign a transaction.
    # This is more secure, as it can control signatures on a message by message basis.
'''    dw = Wallet.wallet()
    dw.load(path="./test_wallet.dec",password="passtest")
    print(dir(dw))
    pq = network.network(url_version="https://test.paxfinancial.ai/data/query",api_key=dw.pubk("test_user"))
    
    
    qUnsigned = {
        'api_key':dw.pubk("test_user"),
        'path':"/",
        'name':"test_dict.json",
        'file_type':'dict',
        'payload':{"test":"val"}}
    qSigned = dw.sign_request(qUnsigned, ["test_user"])    
    assert "__sigs" in qSigned
    fil  = pq.create_entity(qSigned)
'''
    
    
def init():
    global state
    try:
        state['dw'] = Wallet.wallet()
        state['dw'].load(path="/app/.wallet.dec",password="cranium")
        test_url = "https://dev.paxfinancial.ai/data/query"
        api_key = "d674500812231d4cb397d810a380a376f4c9a4f6b5192c2c5621d0d9399f0e2c7308fc6a29e262c5508e52cc0e846b1a3c7ac34cfdb86c16c2a663266f72c8fc"
        state['pq'] = Network(test_url,api_key)
        assert state['pq'].connected() 
        return True
    except Exception as e:
        print(e)
        return False
    
def register():
    global state
    try:
        #'connect_data':{"id":"node-session-test",
        #                            'services':{"id_download_data":{"id":"id_download_data",
        #                                                            "name":"download_data",}},
        #                             "type":"tcpip"}
        
        api_key = "d674500812231d4cb397d810a380a376f4c9a4f6b5192c2c5621d0d9399f0e2c7308fc6a29e262c5508e52cc0e846b1a3c7ac34cfdb86c16c2a663266f72c8fc"
        new_id = None
        name = "node-session-file-"+str(worker_id)+".node"
        message = {'name': name, 
                   'api_key':api_key,
                   'self_id':new_id,

                   'connect_data':{"id":"node-session-test",
                                    'services':{"id_download_data":{"id":"id_download_data",
                                                                    "name":"download_data",}},
                                     "type":"tcpip"}
                  }
        qSigned = state['dw'].sign_request(message, ["sid"])
        state['pq'].register(qSigned)
        state['pq'].listen()
        assert state['pq'].listening()
        return True
    except Exception as e:
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
        list_nodes,
        connect,
        list_sessions,
        store_variable,
        force_disconnect,
        get_disconnect_requests,
        reconnect,
        retrieve_variable,
        purge_network_data
    ]

    results = []
    for i, step in enumerate(steps):
        #print(f"Worker {worker_id}: Running step {step.__name__}")
        result = step()
        results.append(result)
        print(f"worker_http.py_{worker_id}: Step {step.__name__} {'succeeded' if result else 'failed'}")

    with open(f"worker{worker_id}_output.txt", "w") as f:
        for result in results:
            f.write(f"{result}\n")

if __name__ == "__main__":
    worker_id = int(sys.argv[1])
    state={}
    run_all_tests()
