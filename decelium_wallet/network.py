class Network:
    
    def __init__(self, test_url=None, api_key=None):
        pass
    
    def register(self, function_list=None):
        if function_list==None:
            function_list=[]
        return True
    
    def list_nodes(self):
        return True
    
    def connect(self,node_id=None):
        return True
    
    def list_sessions(self):
        return True
    
    def store_variable(self,session_id=None,key=None,value=None):
        return True
    
    def get_variable(self,session_id,key=None):
        return True
    
    def disconnect(self,session_id=None):
        return True
    
    def delete_variable(self,session_id=None,key=None):
        return True