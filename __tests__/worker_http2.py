import sys
import os
import time
from dotenv import load_dotenv

def run_tests(worker_id):
    
    try:
        from decelium_wallet.network import network

        load_dotenv()
        
        DECELIUM_SERVER = os.getenv('DECELIUM_SERVER')
        API_KEY = os.getenv('API_KEY')
        pq = network(DECELIUM_SERVER,API_KEY)
        assert pq is not None        
        
        session_id_main = pq.add_session(DECELIUM_SERVER)
        assert session_id_main is not None
        
        sessions = pq.current_sessions()
        assert len(sessions)==1
        
        pq.register_node() 
        
        time.sleep(1)
        
        nodes = pq.list_nodes()
        assert len(nodes)==5
        
        session_ids = []
        for node in nodes:
            session_id = pq.add_session(node)
            assert session_id is not None
            session_ids.append(session_id)

        sessions = pq.current_sessions()
        assert len(sessions)==6
        for session in sessions:
            assert session in session_ids
        
        print("passed")
        sys.exit(0)    
        
    except Exception as e:
        print(e)
        print("failed")
        sys.exit(1)
    
if __name__ == "__main__":
    worker_id = int(sys.argv[1])
    run_tests(worker_id)    